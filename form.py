import psycopg2
from datetime import date

HOST = "tuxa.sme.utc"
USER = "ed05a008"
PASSWORD = "q0nbsgrSK0IM"
DATABASE = "dbed05a008"

def connect():
    return psycopg2.connect("host=%s dbname=%s user=%s password=%s" %
                            (HOST, DATABASE, USER, PASSWORD))

# ---------------------------------------------------------
# Utility for next ID
# ---------------------------------------------------------

def next_id(cursor, table, column):
    cursor.execute("SELECT COALESCE(MAX(%s), 0) + 1 FROM %s" % (column, table))
    return cursor.fetchone()[0]

# ---------------------------------------------------------
# Individuals
# ---------------------------------------------------------

def add_individual(name, last_name, coords):
    conn = connect()
    cur = conn.cursor()

    eid = next_id(cur, "Entities", "entities_id")
    cur.execute("INSERT INTO Entities VALUES (%s)", (eid,))
    cur.execute(
        "INSERT INTO Individuals VALUES (%s, %s, %s, %s)",
        (eid, name, last_name, coords)
    )

    conn.commit()
    conn.close()
    return eid

def update_coordinates(ind_id, coords):
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        "UPDATE Individuals SET geographic_coordinates=%s WHERE entities_id=%s",
        (coords, ind_id)
    )
    conn.commit()
    conn.close()

# ---------------------------------------------------------
# Communities
# ---------------------------------------------------------

def add_community(name, description, admin_id):
    conn = connect()
    cur = conn.cursor()

    eid = next_id(cur, "Entities", "entities_id")
    mid = next_id(cur, "Membership", "membership_id")

    cur.execute("INSERT INTO Entities VALUES (%s)", (eid,))
    cur.execute(
        "INSERT INTO Communities VALUES (%s, %s, %s)",
        (eid, name, description)
    )

    cur.execute(
        "INSERT INTO Membership VALUES (%s, %s, false, %s, %s)",
        (mid, date.today(), eid, admin_id)
    )

    conn.commit()
    conn.close()
    return eid

def join_community(ind_id, com_id):
    conn = connect()
    cur = conn.cursor()

    mid = next_id(cur, "Membership", "membership_id")
    cur.execute(
        "INSERT INTO Membership VALUES (%s, %s, false, %s, %s)",
        (mid, date.today(), com_id, ind_id)
    )

    conn.commit()
    conn.close()

# ---------------------------------------------------------
# Voting for exclusion
# ---------------------------------------------------------

def vote_exclusion(voter_mid, target_mid):
    conn = connect()
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO Vote VALUES (%s, %s, %s)",
            (voter_mid, target_mid, date.today())
        )

        cur.execute(
            "SELECT COUNT(*) FROM Vote WHERE membership_id2=%s",
            (target_mid,)
        )
        votes = cur.fetchone()[0]

        cur.execute(
            "SELECT targets FROM Membership WHERE membership_id=%s",
            (target_mid,)
        )
        res = cur.fetchone()

        if not res:
            conn.commit()
            return

        community = res[0]

        cur.execute(
            "SELECT COUNT(*) FROM Membership WHERE targets=%s",
            (community,)
        )
        total = cur.fetchone()[0]

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise  # laisse remonter l’erreur (trigger, contrainte, etc.)

    finally:
        cur.close()
        conn.close()


# ---------------------------------------------------------
# Relationships
# ---------------------------------------------------------

def add_relationship(source_id, target_id, description):
    conn = connect()
    cur = conn.cursor()

    rid = next_id(cur, "Relationship", "relationship_id")
    cur.execute(
        "INSERT INTO Relationship VALUES (%s, %s, %s, %s)",
        (rid, description, source_id, target_id)
    )
    conn.commit()
    conn.close()

# ---------------------------------------------------------
# Community links (community to community)
# ---------------------------------------------------------

def add_link(source_com, target_com, description):
    conn = connect()
    cur = conn.cursor()

    lid = next_id(cur, "Link", "link_id")
    cur.execute(
        "INSERT INTO Link VALUES (%s, %s, %s, %s)",
        (lid, description, target_com, source_com)
    )
    conn.commit()
    conn.close()

# ---------------------------------------------------------
# Skills (usable by individuals and communities)
# ---------------------------------------------------------

def add_skill(skill_type):
    conn = connect()
    cur = conn.cursor()

    sid = next_id(cur, "Skill", "skill_id")
    cur.execute("INSERT INTO Skill VALUES (%s, %s)", (sid, skill_type))

    conn.commit()
    conn.close()
    return sid

def declare_expertise(entity_id, skill_id, degree):
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO Expertise VALUES (%s, %s, %s)",
        (entity_id, skill_id, degree)
    )
    conn.commit()
    conn.close()

# ---------------------------------------------------------
# Services
# ---------------------------------------------------------

def add_service(name, description, service_type):
    conn = connect()
    cur = conn.cursor()

    sid = next_id(cur, "Services", "service_id")
    cur.execute(
        "INSERT INTO Services VALUES (%s, %s, %s, %s)",
        (sid, name, description, service_type)
    )

    conn.commit()
    conn.close()
    return sid

def link_service(ind_id, service_id):
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO Individuals_proposes_services VALUES (%s, %s)",
        (service_id, ind_id)
    )

    conn.commit()
    conn.close()

# ---------------------------------------------------------
# Messaging
# ---------------------------------------------------------

def send_message(sender, recipient, content, ref=None):
    conn = connect()
    cur = conn.cursor()

    mid = next_id(cur, "Message", "message_id")
    cur.execute(
        "INSERT INTO Message VALUES (%s, %s, %s, %s, %s)",
        (mid, content, recipient, sender, ref)
    )
    conn.commit()
    conn.close()

# ---------------------------------------------------------
# G1 accounts (individuals and communities)
# ---------------------------------------------------------

def add_g1(entity_id, key):
    conn = connect()
    cur = conn.cursor()

    aid = next_id(cur, "G1account", "account_id")
    cur.execute(
        "INSERT INTO G1account VALUES (%s, %s, %s)",
        (aid, key, entity_id)
    )
    conn.commit()
    conn.close()

