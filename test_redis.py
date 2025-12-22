"""
Script de prueba de conexión a Redis/Memurai
"""
import redis
import sys

def test_redis_connection():
    print("🧪 Prueba de Conexión Redis")
    print("=" * 50)
    
    try:
        # Conectar a Redis/Memurai (sin contraseña por defecto)
        print("\n📡 Conectando a Redis/Memurai...")
        print("   Host: localhost")
        print("   Puerto: 6379")
        
        r = redis.Redis(
            host='localhost',
            port=6379,
            decode_responses=True,
            socket_connect_timeout=5
        )
        
        # Probar conexión
        response = r.ping()
        if response:
            print("✅ Conexión exitosa - PONG recibido\n")
        
        # Probar operaciones básicas
        print("🔧 Probando operaciones básicas...")
        
        # SET
        r.set('test_key', 'VerificarSMS Test')
        print("   ✅ SET: clave guardada")
        
        # GET
        value = r.get('test_key')
        print(f"   ✅ GET: {value}")
        
        # DELETE
        r.delete('test_key')
        print("   ✅ DELETE: clave eliminada")
        
        # Info del servidor
        print("\n📊 Información del servidor:")
        info = r.info('server')
        print(f"   Redis versión: {info.get('redis_version', 'N/A')}")
        print(f"   Modo: {info.get('redis_mode', 'standalone')}")
        print(f"   Uptime: {info.get('uptime_in_seconds', 0)} segundos")
        
        # Probar sesiones con TTL
        print("\n⏱️  Probando expiración de claves (TTL)...")
        r.setex('session_test', 10, 'Esta clave expira en 10 segundos')
        ttl = r.ttl('session_test')
        print(f"   ✅ Clave con expiración creada (TTL: {ttl}s)")
        
        print("\n" + "=" * 50)
        print("✅ Todas las pruebas pasaron exitosamente")
        print("\n🎯 Redis está listo para:")
        print("   - Almacenar sesiones de usuarios")
        print("   - Caché de consultas frecuentes")
        print("   - Rate limiting")
        print("   - Contadores en tiempo real")
        
        return True
        
    except redis.ConnectionError as e:
        print(f"\n❌ Error de conexión: {e}")
        print("\n💡 Verifica que:")
        print("   - Memurai/Redis esté instalado")
        print("   - El servicio esté corriendo")
        print("   - El puerto 6379 esté disponible")
        print("\n🔍 Para verificar el servicio:")
        print("   Get-Service *memurai* -or Get-Service *redis*")
        return False
        
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_redis_connection()
    sys.exit(0 if success else 1)
