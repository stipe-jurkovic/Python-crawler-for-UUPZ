from torpy.http.requests import TorRequests

print('start')


with TorRequests() as tor_requests:
    # We do a first request to ipify.org with a Tor proxy
    print("build circuit #1")
    with tor_requests.get_session() as sess:
        print(sess.request("GET", "https://api.ipify.org/").text)

    # We do a second request to ipify.org with a Tor proxy
    print("build circuit #2")
    with tor_requests.get_session() as sess:
        print(sess.get("https://api.ipify.org/").text)

print('~~success')
