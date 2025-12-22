"""Script temporal para verificar las rutas"""
try:
    from backend.routes.registros import router
    print('✅ Router importado correctamente')
    print(f'Rutas en el router: {len(router.routes)}')
    for r in router.routes:
        if hasattr(r, 'methods') and hasattr(r, 'path'):
            print(f'  - {r.methods} {r.path}')
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
