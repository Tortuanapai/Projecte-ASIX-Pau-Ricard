from database import connect_to_db

def test():
    print("--- INICIANT PROVA DE CONNEXIÓ ---")
    conn = connect_to_db()
    
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT version();")
            version = cur.fetchone()
            print(f"✅ CONNEXIÓ ESTABLERTA!")
            print(f"🖥️ Versió de Postgres: {version[0]}")
            
            cur.execute("SELECT COUNT(*) FROM usuaris_registrats;")
            total = cur.fetchone()
            print(f"📊 Usuaris a la base de dades: {total[0]}")
            
            cur.close()
            conn.close()
            print("--- PROVA FINALITZADA AMB ÈXIT ---")
        except Exception as e:
            print(f"❌ Error executant consulta: {e}")
    else:
        print("❌ NO S'HA POGUT CONNECTAR. Revisa settings.json i que Postgres estigui actiu.")

if __name__ == "__main__":
    test()