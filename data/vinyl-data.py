import os
from dotenv import load_dotenv
import base64
from requests import post, get
import json

popular_albums = [
    'Thriller',
    'The Dark Side of the Moon',
    'Back in Black',
    'The Bodyguard soundtrack',
    'Bat Out of Hell',
    'Led Zeppelin IV',
    'Rumours',
    'Saturday Night Fever soundtrack',
    'The Eagles Greatest Hits 1971-1975',
    'Appetite for Destruction',
    'The Beatles (The White Album)',
    'Hotel California',
    'The Joshua Tree',
    'Born in the U.S.A.',
    'Abbey Road',
    'Sgt. Pepper\'s Lonely Hearts Club Band',
    'Exile on Main St.',
    'The Wall',
    'Purple Rain',
    'Nevermind',
    'Hysteria',
    'The Eminem Show',
    'Back to Black',
    '21',
    'Goodbye Yellow Brick Road',
    'London Calling',
    'Tapestry',
    'American Idiot',
    'The Chronic',
    'Greatest Hits',
    'Jagged Little Pill',
    'Off the Wall',
    'The Doors',
    'Parallel Lines',
    'Never Mind the Bollocks, Here\'s the Sex Pistols',
    'The Rise and Fall of Ziggy Stardust and the Spiders from Mars',
    'Blood on the Tracks',
    'Blue',
    'Houses of the Holy',
    'Bridge over Troubled Water',
    'Ten',
    'Electric Ladyland',
    'The Queen is Dead',
    'Physical Graffiti',
    'Kind of Blue',
    'Tracy Chapman',
    'Songs in the Key of Life',
    'Legend',
    'The Velvet Underground & Nico',
    'A Night at the Opera',
    'Graceland',
    'Synchronicity',
    'The Bends',
    'Automatic for the People',
    'Kid A',
    'Is This It',
    'Funeral',
    'Demon Days',
    'To Pimp a Butterfly',
    'Blonde',
    'Good Kid, M.A.A.D City',
    'My Beautiful Dark Twisted Fantasy',
    'Yeezus',
    'Abbey Road',
    'Revolver',
    'Rubber Soul',
    'Pet Sounds',
    'The Beatles (The White Album)',
    'Blue',
    'Songs in the Key of Life',
    'Rumours',
    'What\'s Going On',
    'Tapestry',
    'Nevermind',
    'The Wall',
    'Exile on Main St.',
    'London Calling',
    'Sgt. Pepper\'s Lonely Hearts Club Band',
    'Appetite for Destruction',
    'The Joshua Tree',
    'Darkness on the Edge of Town',
    'Born in the U.S.A.',
    'Born to Run',
    'Electric Ladyland',
    'Never Mind the Bollocks, Here\'s the Sex Pistols',
    'Blood on the Tracks',
    'Horses',
    'Automatic for the People',
    'Kind of Blue',
    '21',
    '25',
    '1989',
    '24K Magic',
    '4:44',
    'A Brief Inquiry into Online Relationships',
    'After Hours',
    'AM',
    'Anti',
    'Blonde',
    'Blurryface',
    'Carry the Fire',
    'Chromatica',
    'Cleopatra',
    'CTRL',
    'DAMN.',
    'Dangerous Woman',
    'Damn Country Music',
    'Darkness and Light',
    'Death of a Bachelor',
    'Delirium',
    'Divide',
    'Electra Heart',
    'El Mal Querer',
    'Everyday Life',
    'Expectations',
    'Father of the Bride',
    'Flicker',
    'Future Nostalgia',
    'Golden Hour',
    'Hamilton (Original Broadway Cast Recording)',
    'Heartbreak on a Full Moon',
    'High as Hope',
    'Hozier',
    'I Like It When You Sleep, for You Are So Beautiful yet So Unaware of It',
    'In the Lonely Hour',
    'Is This It',
    'Joanne',
    'KOD',
    'Lemonade',
    'Let\'s Rock',
    'Lonerism',
    'Loud',
    'M A N I A',
    'Man on the Moon III: The Chosen',
    'Melodrama',
    'Montero',
    'My Beautiful Dark Twisted Fantasy',
    'Native',
    'Night Visions',
    'Norman Fucking Rockwell!',
    'Now That\'s What I Call Music! 73',
    'Nothing Was the Same',
    'One of the Boys',
    'One More Light',
    'Overexposed',
    'Palo Santo',
    'Pink Friday',
    'Plastic Hearts',
    'Positions',
    'Pure Heroine',
    'Red',
    'Reputation',
    'Revival',
    'Sigh No More',
    'Sour',
    'Starboy',
    'Stoney',
    'Sweetener',
    'Take Care',
    'Thank U, Next',
    'The 20/20 Experience',
    'The Album',
    'The ArchAndroid',
    'The Bones of What You Believe',
    'The Heist',
    'The Life of Pablo',
    'The Lumineers',
    'The Marshall Mathers LP 2',
    'The Pinkprint',
    'The Search',
    'The Slow Rush',
    'The Thrill of It All',
    'The Weight of These Wings',
    'Trench',
    'Trilogy',
    'Views',
    'When We All Fall Asleep, Where Do We Go?',
    'Witness',
    'X',
    'Yours to Keep'
]

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")


def get_token():
    auth_str = client_id + ":" + client_secret
    auth_bytes = auth_str.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token


def get_auth_header(token):
    return {"Authorization": "Bearer " + token}


def search_for_album(token, album_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={album_name}&type=album&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["albums"]["items"]
    # print(json_result)

    if len(json_result) == 0:
        print("No album with this name")
        return None

    return json_result[0]


token = get_token()
for album in popular_albums:
    result = search_for_album(token, album)

    print(result["name"], result["images"][0]
          ["url"], result["artists"][0]["name"], result["release_date"][0:4])
