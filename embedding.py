
import psycopg2
import ollama

CONN_INFO = "host=localhost port=5433 dbname=at_data_db user=anasteysha password=abc"


def calcEmbed(text, model="nomic-embed-text"):
    response = ollama.embeddings(
        model=model,
        prompt=text or ""
    )
    return response["embedding"]


def updateVector():
    conn = None
    cur = None

    try:
        conn = psycopg2.connect(CONN_INFO)
        conn.autocommit = True
        cur = conn.cursor()

        cur.execute("""
            SELECT id, page, title, context
            FROM at_data
            WHERE page_vector IS NULL
               OR title_vector IS NULL
               OR context_vector IS NULL
            ORDER BY id
        """)

        rows = cur.fetchall()
        total = len(rows)

        print(f"Updating {total} records...")

        for index, row in enumerate(rows, start=1):
            row_id, page, title, context = row

            page_vec = calcEmbed(page)
            title_vec = calcEmbed(title)
            context_vec = calcEmbed(context)

            cur.execute("""
                UPDATE at_data
                SET page_vector = %s,
                    title_vector = %s,
                    context_vector = %s
                WHERE id = %s
            """, (page_vec, title_vec, context_vec, row_id))

            print(f"Updated {index}/{total} (ID: {row_id})")

        print("All embeddings updated successfully!")

    except Exception as e:
        print("Error:", e)

    finally:
        if cur is not None:
            cur.close()

        if conn is not None:
            conn.close()


if __name__ == "__main__":
    updateVector()
