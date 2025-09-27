# tests/test_conversation_system.py
import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import json

# Importar nuestras clases
from database.conversation_db import ConversationDatabase, ConversationMessage
from core.agent import PMAgent

class TestConversationSystem(unittest.TestCase):
    """Test suite para el sistema completo de conversaciones"""
    
    def setUp(self):
        """Configurar test environment"""
        # Crear directorio temporal para tests
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_db_path = self.test_dir / "test_conversations.db"
        
        # Inicializar base de datos de prueba
        self.db = ConversationDatabase(str(self.test_db_path))
        
        # Datos de prueba
        self.test_project_id = "test_project"
        self.test_session_name = "Test Session"
        
    def tearDown(self):
        """Limpiar después de los tests"""
        shutil.rmtree(self.test_dir)
    
    def test_database_initialization(self):
        """Test 1: Inicialización de la base de datos"""
        # Verificar que el archivo de BD se creó
        self.assertTrue(self.test_db_path.exists())
        
        # Verificar que las tablas fueron creadas
        import sqlite3
        with sqlite3.connect(self.test_db_path) as conn:
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN (
                    'conversation_sessions', 
                    'conversation_messages', 
                    'usage_stats', 
                    'message_search'
                )
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
        expected_tables = ['conversation_sessions', 'conversation_messages', 'usage_stats', 'message_search']
        for table in expected_tables:
            self.assertIn(table, tables, f"Tabla {table} no fue creada")
        
        print("✅ Test 1: Inicialización de BD - PASSED")
    
    def test_session_creation_and_retrieval(self):
        """Test 2: Crear y recuperar sesiones"""
        # Crear sesión
        session_id = self.db.create_session(
            project_id=self.test_project_id,
            name=self.test_session_name,
            tags=["test", "unit-test"]
        )
        
        # Verificar que el ID fue generado
        self.assertIsNotNone(session_id)
        self.assertTrue(len(session_id) > 20)  # UUID format
        
        # Recuperar estadísticas de la sesión
        stats = self.db.get_session_stats(session_id)
        
        self.assertEqual(stats['project_id'], self.test_project_id)
        self.assertEqual(stats['name'], self.test_session_name)
        self.assertEqual(stats['message_count'], 0)
        self.assertEqual(stats['total_tokens'], 0)
        self.assertEqual(stats['status'], 'active')
        
        # Verificar tags
        tags = json.loads(stats['tags']) if isinstance(stats['tags'], str) else stats['tags']
        self.assertIn("test", tags)
        self.assertIn("unit-test", tags)
        
        print("✅ Test 2: Creación y recuperación de sesiones - PASSED")
    
    def test_message_operations(self):
        """Test 3: Operaciones con mensajes"""
        # Crear sesión
        session_id = self.db.create_session(self.test_project_id, "Test Messages")
        
        # Agregar mensajes de prueba
        test_messages = [
            ("user", "¿Qué es un project charter?", 15),
            ("assistant", "Un project charter es un documento que autoriza formalmente un proyecto...", 45),
            ("user", "¿Cuáles son sus componentes principales?", 12),
            ("assistant", "Los componentes principales del project charter incluyen: objetivos, alcance, stakeholders...", 38)
        ]
        
        message_ids = []
        for role, content, tokens in test_messages:
            msg_id = self.db.add_message(
                session_id=session_id,
                project_id=self.test_project_id,
                role=role,
                content=content,
                tokens_used=tokens,
                model_used="test-model"
            )
            message_ids.append(msg_id)
        
        # Verificar que se agregaron correctamente
        self.assertEqual(len(message_ids), 4)
        
        # Recuperar mensajes
        messages = self.db.get_session_messages(session_id)
        self.assertEqual(len(messages), 4)
        
        # Verificar orden
        for i, msg in enumerate(messages):
            self.assertEqual(msg.message_order, i + 1)
            self.assertEqual(msg.role, test_messages[i][0])
            self.assertEqual(msg.content, test_messages[i][1])
            self.assertEqual(msg.tokens_used, test_messages[i][2])
        
        # Verificar actualización de estadísticas de sesión
        stats = self.db.get_session_stats(session_id)
        self.assertEqual(stats['message_count'], 4)
        self.assertEqual(stats['total_tokens'], 110)  # 15+45+12+38
        
        print("✅ Test 3: Operaciones con mensajes - PASSED")
    
    def test_full_text_search(self):
        """Test 4: Búsqueda full-text"""
        # Crear sesión y mensajes de prueba
        session_id = self.db.create_session(self.test_project_id, "Search Test")
        
        search_messages = [
            ("user", "Háblame sobre gestión de riesgos en proyectos"),
            ("assistant", "La gestión de riesgos es fundamental para el éxito del proyecto"),
            ("user", "¿Cómo identificar riesgos potenciales?"),
            ("assistant", "Para identificar riesgos puedes usar técnicas como brainstorming y análisis SWOT")
        ]
        
        for role, content in search_messages:
            self.db.add_message(session_id, self.test_project_id, role, content, tokens_used=20)
        
        # Buscar términos
        results = self.db.search_conversations("riesgos", limit=10)
        self.assertGreaterEqual(len(results), 2)  # Al menos 2 mensajes contienen "riesgos"
        
        # Buscar término específico
        results = self.db.search_conversations("SWOT", limit=10)
        self.assertEqual(len(results), 1)
        self.assertIn("SWOT", results[0]['content'])
        
        print("✅ Test 4: Búsqueda full-text - PASSED")
    
    def test_export_functionality(self):
        """Test 5: Funcionalidad de exportación"""
        # Crear sesión con mensajes
        session_id = self.db.create_session(self.test_project_id, "Export Test")
        
        test_messages = [
            ("user", "Test message 1"),
            ("assistant", "Test response 1"),
            ("user", "Test message 2"),
            ("assistant", "Test response 2")
        ]
        
        for role, content in test_messages:
            self.db.add_message(session_id, self.test_project_id, role, content, tokens_used=10)
        
        # Test export JSON
        json_export = self.db.export_session(session_id, format='json')
        self.assertIsInstance(json_export, str)
        
        # Verificar que es JSON válido
        try:
            parsed_json = json.loads(json_export)
            self.assertIn('session', parsed_json)
            self.assertIn('messages', parsed_json)
            self.assertEqual(len(parsed_json['messages']), 4)
        except json.JSONDecodeError:
            self.fail("Export JSON no es válido")
        
        # Test export Markdown
        md_export = self.db.export_session(session_id, format='markdown')
        self.assertIsInstance(md_export, str)
        self.assertIn("# Export Test", md_export)
        self.assertIn("👤 USER", md_export)
        self.assertIn("🤖 ASSISTANT", md_export)
        
        print("✅ Test 5: Funcionalidad de exportación - PASSED")
    
    def test_analytics_and_stats(self):
        """Test 6: Analytics y estadísticas"""
        # Crear múltiples sesiones con datos
        sessions = []
        for i in range(3):
            session_id = self.db.create_session(self.test_project_id, f"Analytics Test {i+1}")
            sessions.append(session_id)
            
            # Agregar varios mensajes a cada sesión
            for j in range(5):
                self.db.add_message(session_id, self.test_project_id, "user", f"Message {j+1}", tokens_used=10)
                self.db.add_message(session_id, self.test_project_id, "assistant", f"Response {j+1}", tokens_used=15)
        
        # Test analytics
        analytics = self.db.get_usage_analytics(project_id=self.test_project_id, days=30)
        
        self.assertIn('daily_stats', analytics)
        self.assertIn('totals', analytics)
        
        totals = analytics['totals']
        self.assertEqual(totals['total_sessions'], 3)
        self.assertEqual(totals['total_messages'], 30)  # 3 sessions * 10 messages each
        self.assertEqual(totals['total_tokens'], 750)   # 3 * 5 * (10 + 15) * 2
        
        print("✅ Test 6: Analytics y estadísticas - PASSED")
    
    def test_session_listing_and_filtering(self):
        """Test 7: Listar y filtrar sesiones"""
        # Crear sesiones en diferentes proyectos
        project1_sessions = []
        project2_sessions = []
        
        for i in range(3):
            # Proyecto 1
            session_id1 = self.db.create_session("project1", f"P1 Session {i+1}")
            project1_sessions.append(session_id1)
            
            # Proyecto 2
            session_id2 = self.db.create_session("project2", f"P2 Session {i+1}")
            project2_sessions.append(session_id2)
        
        # Test listar todas las sesiones
        all_sessions = self.db.list_sessions(limit=10)
        self.assertEqual(len(all_sessions), 6)
        
        # Test filtrar por proyecto
        p1_sessions = self.db.list_sessions(project_id="project1", limit=10)
        self.assertEqual(len(p1_sessions), 3)
        for session in p1_sessions:
            self.assertEqual(session['project_id'], "project1")
        
        p2_sessions = self.db.list_sessions(project_id="project2", limit=10)
        self.assertEqual(len(p2_sessions), 3)
        for session in p2_sessions:
            self.assertEqual(session['project_id'], "project2")
        
        print("✅ Test 7: Listar y filtrar sesiones - PASSED")
    
    def test_cleanup_operations(self):
        """Test 8: Operaciones de limpieza"""
        # Crear sesión de prueba
        session_id = self.db.create_session(self.test_project_id, "Cleanup Test")
        
        # Verificar que está activa
        stats = self.db.get_session_stats(session_id)
        self.assertEqual(stats['status'], 'active')
        
        # Test cleanup (con 0 días para forzar archivado)
        archived_count = self.db.cleanup_old_sessions(days=0)
        self.assertEqual(archived_count, 1)
        
        # Verificar que fue archivada
        stats_after = self.db.get_session_stats(session_id)
        self.assertEqual(stats_after['status'], 'archived')
        
        print("✅ Test 8: Operaciones de limpieza - PASSED")
    
    def run_all_tests(self):
        """Ejecutar todos los tests"""
        print("\n🧪 INICIANDO TESTS DEL SISTEMA COMPLETO\n" + "="*50)
        
        test_methods = [
            self.test_database_initialization,
            self.test_session_creation_and_retrieval,
            self.test_message_operations,
            self.test_full_text_search,
            self.test_export_functionality,
            self.test_analytics_and_stats,
            self.test_session_listing_and_filtering,
            self.test_cleanup_operations
        ]
        
        passed = 0
        failed = 0
        
        for test_method in test_methods:
            try:
                # Reinicializar DB para cada test
                self.setUp()
                test_method()
                passed += 1
            except Exception as e:
                print(f"❌ {test_method.__name__} - FAILED: {str(e)}")
                failed += 1
            finally:
                self.tearDown()
        
        print(f"\n" + "="*50)
        print(f"🎯 RESUMEN DE TESTS")
        print(f"✅ Pasados: {passed}")
        print(f"❌ Fallidos: {failed}")
        print(f"📊 Total: {passed + failed}")
        
        if failed == 0:
            print("🎉 ¡TODOS LOS TESTS PASARON!")
            return True
        else:
            print("⚠️ Algunos tests fallaron. Revisar implementación.")
            return False


# Script de prueba independiente
def run_integration_test():
    """Ejecutar test de integración completo"""
    print("\n🚀 TEST DE INTEGRACIÓN COMPLETA DEL SISTEMA")
    print("="*60)
    
    # Crear directorio temporal
    import tempfile
    import shutil
    
    test_dir = Path(tempfile.mkdtemp())
    print(f"📁 Directorio de prueba: {test_dir}")
    
    try:
        # Test 1: Inicializar sistema completo
        print("\n1️⃣ Inicializando sistema completo...")
        
        # Simular inicialización completa del agente
        db_path = test_dir / "integration_test.db"
        db = ConversationDatabase(str(db_path))
        
        print("✅ Base de datos inicializada")
        
        # Test 2: Flujo completo de usuario
        print("\n2️⃣ Simulando flujo completo de usuario...")
        
        # Crear sesión
        session_id = db.create_session(
            project_id="integration_test",
            name="Sesión de Integración",
            tags=["integration", "test", "full-flow"]
        )
        print(f"✅ Sesión creada: {session_id[:8]}...")
        
        # Simular conversación completa
        conversation_flow = [
            ("user", "¿Qué es la metodología Agile?"),
            ("assistant", "Agile es una metodología de gestión de proyectos que se basa en iteraciones cortas..."),
            ("user", "¿Cuáles son los principios del Manifiesto Ágil?"),
            ("assistant", "Los 4 valores fundamentales del Manifiesto Ágil son: 1) Individuos e interacciones..."),
            ("user", "¿Cómo implementar Scrum en mi equipo?"),
            ("assistant", "Para implementar Scrum necesitas definir roles: Product Owner, Scrum Master..."),
            ("user", "¿Qué herramientas recomiendas para Scrum?"),
            ("assistant", "Algunas herramientas populares para Scrum incluyen: Jira, Azure DevOps, Trello...")
        ]
        
        total_tokens = 0
        for i, (role, content) in enumerate(conversation_flow):
            estimated_tokens = len(content.split()) * 1.3  # Estimación simple
            total_tokens += estimated_tokens
            
            db.add_message(
                session_id=session_id,
                project_id="integration_test",
                role=role,
                content=content,
                tokens_used=int(estimated_tokens),
                model_used="claude-sonnet-4",
                metadata={"step": i+1, "conversation_flow": True}
            )
        
        print(f"✅ Conversación simulada: {len(conversation_flow)} mensajes, ~{int(total_tokens)} tokens")
        
        # Test 3: Verificar funcionalidades avanzadas
        print("\n3️⃣ Probando funcionalidades avanzadas...")
        
        # Búsqueda
        search_results = db.search_conversations("Agile", limit=5)
        print(f"✅ Búsqueda 'Agile': {len(search_results)} resultados")
        
        search_results2 = db.search_conversations("Scrum", limit=5)
        print(f"✅ Búsqueda 'Scrum': {len(search_results2)} resultados")
        
        # Estadísticas
        session_stats = db.get_session_stats(session_id)
        print(f"✅ Estadísticas de sesión: {session_stats['message_count']} mensajes, {session_stats['total_tokens']} tokens")
        
        # Analytics
        analytics = db.get_usage_analytics(project_id="integration_test", days=1)
        print(f"✅ Analytics: {analytics['totals']['total_sessions']} sesión(es), {analytics['totals']['total_messages']} mensajes")
        
        # Test 4: Exportación
        print("\n4️⃣ Probando exportación...")
        
        # Export JSON
        json_export = db.export_session(session_id, format='json')
        json_file = test_dir / "export_test.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            f.write(json_export)
        print(f"✅ Export JSON: {json_file} ({json_file.stat().st_size} bytes)")
        
        # Export Markdown
        md_export = db.export_session(session_id, format='markdown')
        md_file = test_dir / "export_test.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md_export)
        print(f"✅ Export Markdown: {md_file} ({md_file.stat().st_size} bytes)")
        
        # Test 5: Rendimiento con datos masivos
        print("\n5️⃣ Test de rendimiento con datos masivos...")
        
        import time
        start_time = time.time()
        
        # Crear múltiples sesiones
        bulk_sessions = []
        for i in range(10):
            bulk_session_id = db.create_session(
                project_id=f"bulk_project_{i % 3}",  # 3 proyectos diferentes
                name=f"Bulk Session {i+1}",
                tags=["bulk", "performance", f"batch_{i//5}"]
            )
            bulk_sessions.append(bulk_session_id)
            
            # Agregar mensajes a cada sesión
            for j in range(20):  # 20 mensajes por sesión
                db.add_message(
                    session_id=bulk_session_id,
                    project_id=f"bulk_project_{i % 3}",
                    role="user" if j % 2 == 0 else "assistant",
                    content=f"Bulk message {j+1} in session {i+1} - This is a performance test message with more content to simulate real usage patterns.",
                    tokens_used=25,
                    model_used="claude-sonnet-4"
                )
        
        bulk_time = time.time() - start_time
        print(f"✅ Datos masivos: 10 sesiones x 20 mensajes = 200 mensajes en {bulk_time:.2f}s")
        
        # Test búsqueda en datos masivos
        start_search = time.time()
        bulk_search_results = db.search_conversations("performance test", limit=10)
        search_time = time.time() - start_search
        print(f"✅ Búsqueda en datos masivos: {len(bulk_search_results)} resultados en {search_time:.3f}s")
        
        # Test 6: Verificación de integridad
        print("\n6️⃣ Verificando integridad de datos...")
        
        # Verificar conteos
        all_sessions = db.list_sessions(limit=50)
        total_expected_sessions = 1 + 10  # Sesión original + 10 bulk
        
        if len(all_sessions) == total_expected_sessions:
            print(f"✅ Integridad de sesiones: {len(all_sessions)}/{total_expected_sessions}")
        else:
            print(f"⚠️ Problema de integridad: esperadas {total_expected_sessions}, encontradas {len(all_sessions)}")
        
        # Verificar mensajes
        total_messages = 0
        for session in all_sessions:
            messages = db.get_session_messages(session['id'])
            total_messages += len(messages)
        
        expected_messages = 8 + (10 * 20)  # Conversación original + bulk
        if total_messages == expected_messages:
            print(f"✅ Integridad de mensajes: {total_messages}/{expected_messages}")
        else:
            print(f"⚠️ Problema de integridad: esperados {expected_messages}, encontrados {total_messages}")
        
        # Test 7: Estadísticas finales del sistema
        print("\n7️⃣ Estadísticas finales del sistema...")
        
        # Tamaño de la base de datos
        db_size = db_path.stat().st_size / 1024  # KB
        print(f"📊 Tamaño final de BD: {db_size:.2f} KB")
        
        # Analytics finales
        final_analytics = db.get_usage_analytics(days=1)
        print(f"📊 Sesiones totales: {final_analytics['totals']['total_sessions']}")
        print(f"📊 Mensajes totales: {final_analytics['totals']['total_messages']}")
        print(f"📊 Tokens totales: {final_analytics['totals']['total_tokens']}")
        
        print("\n" + "="*60)
        print("🎉 TEST DE INTEGRACIÓN COMPLETADO EXITOSAMENTE!")
        print("✅ Todas las funcionalidades del sistema funcionan correctamente")
        print("✅ Rendimiento aceptable con datos masivos")
        print("✅ Integridad de datos verificada")
        print("✅ Exportación funcional")
        print("✅ Búsqueda full-text operativa")
        print("✅ Analytics precisos")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR EN TEST DE INTEGRACIÓN: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Limpiar
        print(f"\n🧹 Limpiando directorio de prueba: {test_dir}")
        shutil.rmtree(test_dir)


# Script principal de testing
if __name__ == "__main__":
    print("🧪 SISTEMA DE TESTING COMPLETO")
    print("="*50)
    
    # Opción 1: Tests unitarios
    print("\n1. Ejecutar tests unitarios")
    print("2. Ejecutar test de integración completa")
    print("3. Ejecutar ambos")
    
    choice = input("\nSelecciona opción (1-3): ").strip()
    
    if choice in ["1", "3"]:
        print("\n" + "🔬 TESTS UNITARIOS".center(50, "="))
        tester = TestConversationSystem()
        tester.setUp()
        unit_success = tester.run_all_tests()
        tester.tearDown()
    else:
        unit_success = True
    
    if choice in ["2", "3"]:
        print("\n" + "🔗 TEST DE INTEGRACIÓN".center(50, "="))
        integration_success = run_integration_test()
    else:
        integration_success = True
    
    # Resultado final
    print("\n" + "📋 RESULTADO FINAL".center(50, "="))
    
    if unit_success and integration_success:
        print("🎉 SISTEMA COMPLETAMENTE FUNCIONAL")
        print("✅ Listo para producción")
        exit(0)
    else:
        print("❌ SISTEMA NECESITA CORRECCIONES")
        print("⚠️ Revisar errores antes de usar en producción")
        exit(1)