from postgres import get_cursor, commit, get_conn
import logging


def insert_book_details(book_details: dict):
    try:
        conn = get_conn()
        cur = get_cursor(conn)
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
        commit(conn)
        cur.close()
    except Exception as e:
        logging.error(str(e))
        cur.close()
        return False
    return True

def get_book_details(book_id: int):
    try:
        conn = get_conn()
        cur = get_cursor(conn)
        cur.execute('SELECT * from books where book_id = %s', (book_id,))
        columns = [column[0] for column in cur.description]
        books = cur.fetchall()
        cur.close()
        if books:
            return serialize_book(dict(zip(columns, books[0])))
        return None
    except Exception as e:
        logging.error(str(e))
        cur.close()
    


def get_all_history():
    try:
        conn = get_conn()
        cur = get_cursor(conn)
        cur.execute('SELECT * from books')
        columns = [column[0] for column in cur.description]
        books = cur.fetchall()
        if books:
            return [serialize_book(dict(zip(columns, book))) for book in books]
        cur.close()
        return []
    except Exception as e:
        logging.error(str(e))
        cur.close()
    

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

