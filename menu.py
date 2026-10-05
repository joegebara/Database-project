import form
import reports

def choose_user():
    print("Individuals:")
    inds = reports.list_individuals()
    for (eid, name, last_name) in inds:
        print("%s - %s %s" % (eid, name, last_name))
    print("0 - I am not in the database")

    choice = input("Who are you? ")

    if choice == "0":
        name = input("First name: ")
        last_name = input("Last name: ")
        coords = int(input("Coordinates: "))
        eid = form.add_individual(name, last_name, coords)
        print("Added with ID:", eid)
        return eid

    return int(choice)


# Search Menu

def menu_search():
    print("\nSearch:")
    print("1 - Individuals")
    print("2 - Communities")
    print("3 - Skills")
    print("4 - Services")

    c = input("Choice: ")
    text = input("Search text: ")

    if c == "1":
        rows = reports.search_individuals(text)
    elif c == "2":
        rows = reports.search_communities(text)
    elif c == "3":
        rows = reports.search_skills(text)
    elif c == "4":
        rows = reports.search_services(text)
    else:
        return

    for r in rows:
        print(r)


# Add community-to-community link


def menu_com_link():
    print("Declare link: Community -> Community")

    rows = reports.allcommunity_view()

    for row in rows:
        print(row)

    src = int(input("Source community ID: "))

    for row in rows:
        print(row)
    
    tgt = int(input("Target community ID: "))
    desc = input("Description: ")
    form.add_link(src, tgt, desc)
    print("Link added.")


# Add skill for a community


def menu_com_skill():
    print("Add a skill to a community")

    rows = reports.allcommunity_view()

    for row in rows:
        print(row)
        
    com = int(input("Community ID: "))
    skill = input("Skill type: ")
    sid = form.add_skill(skill)
    degree = int(input("Expertise (1-5): "))
    form.declare_expertise(com, sid, degree)
    print("Skill registered for community.")


# Add G1 key for a community


def menu_com_g1():
    print("Add G1 key for community")
    com = int(input("Community ID: "))
    key = input("Public key: ")
    form.add_g1(com, key)
    print("Key registered.")


# OpenStreetMap link

def menu_osm():
    ind = int(input("Individual ID: "))
    coords = None
    liste = reports.load_coordinates()
    for (eid, c) in liste:
        if eid == ind:
            coords = c
            break
    if coords is None:
        print("No coordinates found.")
        return
    print("OSM link:", reports.osm_link(coords))


# Main Menus

def send_message_menu(eid):
    print("\nChoose a recipient:")
    persons = reports.list_individuals()

    for (pid, name, last_name) in persons:
        print("%s - %s %s" % (pid, name, last_name))

    rid = int(input("Recipient ID: "))

    content = input("Content: ")
    ref = input("Reference (empty if none): ")
    ref = None if ref.strip() == "" else int(ref)

    form.send_message(eid, rid, content, ref)
    print("Message sent.")


def vote_menu(eid):
    print("\nCommunities you belong to:")
    mems = reports.memberships_of(eid)

    if not mems:
        print("You are not in any community.")
        return

    for (mid, com_id, com_name) in mems:
        print("%s - %s" % (com_id, com_name))

    com_choice = int(input("Which community? (enter community ID) : "))

    # find membership_id automatically
    voter_mid = reports.membership_id_of(eid, com_choice)

    if voter_mid is None:
        print("You are not a member of this community.")
        return

    print("\nMembers of this community:")

    # display the members of the community to find the target
    members = reports.list_mumber_of_community(com_choice)

    for (mid, ind_id, name, last_name) in members:
        print("%s - %s %s" % (ind_id, name, last_name))

    target_eid = int(input("Person to exclude (enter individual ID): "))

    # find membership_id of the target
    target_mid = reports.membership_id_of(target_eid, com_choice)

    if target_mid is None:
        print("This person is not in that community.")
        return

    form.vote_exclusion(voter_mid, target_mid)
    print("Vote recorded.")


def message_view(eid):
    threads = reports.message_thread(eid)
    for chain in threads:
        print("\nThread:")
        for msg in chain:
            if msg:
                print("ID:", msg[0], "| from:", msg[2], "| to:", msg[3], "|", msg[1])

def main_menu(eid):
    while True:
        print("\nMain Menu")
        print("1 - My communities")
        print("2 - Send message")
        print("3 - Message view")
        print("4 - Declare skill (individual)")
        print("5 - Offer service")
        print("6 - Add relationship")
        print("7 - Proximity view")
        print("8 - Create community")
        print("9 - Join community")
        print("10 - Vote exclusion")
        print("11 - Add G1 key (individual)")
        print("12 - Search")
        print("13 - Update my coordinates")
        print("14 - Declare community link")
        print("15 - Add skill to community")
        print("16 - Add G1 key to community")
        print("17 - Show OpenStreetMap link")
        print("0 - Quit")

        c = input("Choice: ")

        if c == "1":
            rows = reports.community_view(eid)

            if not rows:
                print("No communities")
            else:
                print("\nYour communities:")
                for mid, name, exclued in rows:
                    status = "Excluded" if exclued else "Active"
                    print(f"ID: {mid:<5} | {name:<20} | {status}")

        elif c == "2":
            send_message_menu(eid)

        elif c == "3":
            message_view(eid)

        elif c == "4":
            skill = input("Skill type: ")
            sid = form.add_skill(skill)
            degree = int(input("Expertise (1-5): "))
            form.declare_expertise(eid, sid, degree)

        elif c == "5":
            name = input("Service name: ")
            desc = input("Description: ")
            typ = input("Type: ")
            sid = form.add_service(name, desc, typ)
            form.link_service(eid, sid)

        elif c == "6":
            tgt = int(input("Target individual: "))
            desc = input("Description: ")
            form.add_relationship(eid, tgt, desc)

        elif c == "7":
            prox = reports.proximity_view()
            if not prox:
                print("No individuals within 1km")
            for p in prox:
                print(p)

        elif c == "8":
            name = input("Name: ")
            desc = input("Description: ")
            cid = form.add_community(name, desc, eid)
            print("Created:", cid)

        elif c == "9":
            print("\nAvailable communities:")
            rows = reports.list_communities()
            for (cid, name, desc) in rows:
                print(f"{cid} - {name}")

            com = int(input("Community ID: "))
            form.join_community(eid, com)
            print ("Joined",com)

        elif c == "10":
            vote_menu(eid)

        elif c == "11":
            key = input("Public key: ")
            form.add_g1(eid, key)

        elif c == "12":
            menu_search()

        elif c == "13":
            coords = int(input("New coordinates: "))
            form.update_coordinates(eid, coords)

        elif c == "14":
            menu_com_link()

        elif c == "15":
            menu_com_skill()

        elif c == "16":
            menu_com_g1()

        elif c == "17":
            menu_osm()

        elif c == "0":
            break

def main():
    eid = choose_user()
    main_menu(eid)

if __name__ == "__main__":
    main()

