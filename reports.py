import psycopg2

HOST = "tuxa.sme.utc"
USER = "ed05a008"
PASSWORD = "q0nbsgrSK0IM"
DATABASE = "dbed05a008"

def connect():
    return psycopg2.connect("host=%s dbname=%s user=%s password=%s" %
                            (HOST, DATABASE, USER, PASSWORD))


# Basic listings

def list_individuals():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT entities_id, name, last_name FROM Individuals ORDER BY name")
    rows = cur.fetchall()
    conn.close()
    return rows

def list_communities():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT entities_id, name, description FROM Communities ORDER BY name")
    rows = cur.fetchall()
    conn.close()
    return rows


# Searching


def search_individuals(text):
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        "SELECT entities_id, name, last_name FROM Individuals "
        "WHERE name ILIKE %s OR last_name ILIKE %s",
        ("%" + text + "%", "%" + text + "%")
    )
    rows = cur.fetchall()
    conn.close()
    return rows

def search_communities(text):
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        "SELECT entities_id, name FROM Communities WHERE name ILIKE %s",
        ("%" + text + "%",)
    )
    rows = cur.fetchall()
    conn.close()
    return rows

def search_skills(text):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT skill_id, skill_type FROM Skill WHERE skill_type ILIKE %s",
                ("%" + text + "%",))
    rows = cur.fetchall()
    conn.close()
    return rows

def search_services(text):
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        "SELECT service_id, name FROM Services WHERE name ILIKE %s",
        ("%" + text + "%",)
    )
    rows = cur.fetchall()
    conn.close()
    return rows


# Community View

def community_view(ind_id): #only the communities of eid
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT M.membership_id, C.name, M.exclued
        FROM Membership M
        JOIN Communities C ON M.targets = C.entities_id
        WHERE M.declares=%s
    """, (ind_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def allcommunity_view():
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT *
        FROM Communities
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

def list_mumber_of_community(com_choice):
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT M.membership_id, I.entities_id, I.name, I.last_name
        FROM Membership M
        JOIN Individuals I ON M.declares = I.entities_id
        WHERE M.targets=%s
    """, (com_choice,))
    members = cur.fetchall()
    conn.close()
    return members 

# Membership view 

def memberships_of(ind_id): #display the membership of an individual
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT M.membership_id, C.entities_id, C.name
        FROM Membership M
        JOIN Communities C ON M.targets = C.entities_id
        WHERE M.declares = %s
        ORDER BY C.name
    """, (ind_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def membership_id_of(ind_id, community_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT membership_id
        FROM Membership
        WHERE declares=%s AND targets=%s
    """, (ind_id, community_id))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


# Messaging threads

def fetch_message(mid):
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        "SELECT message_id, message_content, send_by, addressed_to, reference "
        "FROM Message WHERE message_id=%s",
        (mid,)
    )
    row = cur.fetchone()
    conn.close()
    return row

def message_thread(entity_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT message_id
        FROM Message
        WHERE addressed_to=%s OR send_by=%s
        ORDER BY message_id
    """, (entity_id, entity_id))
    rows = cur.fetchall()
    conn.close()

    threads = []
    for (mid,) in rows:
        chain = []
        current = mid
        while current:
            row = fetch_message(current)
            chain.append(row)
            current = row[4]
        chain.reverse()
        threads.append(chain)

    return threads


# Proximity

def load_coordinates():
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        "SELECT entities_id, geographic_coordinates FROM Individuals "
        "WHERE geographic_coordinates IS NOT NULL"
    )
    rows = cur.fetchall()
    conn.close()
    return rows

def distance(a, b):
    return abs(a - b)

def proximity_view():
    coords = load_coordinates()
    result = []

    for i in range(len(coords)):
        for j in range(i + 1, len(coords)):
            d = distance(coords[i][1], coords[j][1])
            if d < 1000:
                result.append((coords[i][0], coords[j][0], d))

    return result


# OpenStreetMap links

def osm_link(coord):
    s = str(coord)
    lat = float(s) / 10000.0
    lon = 0.0
    zoom = 15
    return f"https://www.openstreetmap.org/#map={zoom}/{lat}/{lon}"

