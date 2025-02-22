from postgres import get_cursor, commit, close_connection


def insert_book_details(book_details: dict):
    try:
        cur = get_cursor()
        cur.execute('INSERT INTO books (book_id, title, author, language, summary, sentiment, key_characters, book_text)'
                'VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                (
                    book_details['book_id'],
                    book_details['title'],
                    book_details['author'],
                    book_details['language'],
                    book_details['summary'],
                    book_details['sentiment'],
                    book_details['key_characters'],
                    book_details['book_text'])
                )
        commit()
        cur.close()
        close_connection()
    except Exception as e:
        print(str(e))
        cur.close()
        return False
    return True

def get_book_details(book_id: int):
    try:
        cur = get_cursor()
        cur.execute('SELECT * from books where book_id = %s', (book_id,))
        columns = [column[0] for column in cur.description]
        books = cur.fetchall()
        if books:
            return serialize_book(dict(zip(columns, books[0])))
        return None
    except Exception as e:
        print(str(e))
    cur.close()
    close_connection()


def get_all_history():
    try:
        cur = get_cursor()
        cur.execute('SELECT * from books')
        columns = [column[0] for column in cur.description]
        books = cur.fetchall()
        if books:
            return [serialize_book(dict(zip(columns, book))) for book in books]
        return []
    except Exception as e:
        print(str(e))
    cur.close()
    close_connection()

def serialize_book(book):
    return {
        'id': book['id'],
        'book_id': book['book_id'],
        'title': book['title'],
        'author': book['author'],
        'language': book['language'],
        'summary': book['summary'],
        'sentiment': book['sentiment'],
        'key_characters': book['key_characters'],
        'book_text': book['book_text']
    }

