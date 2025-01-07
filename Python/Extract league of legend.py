import requests
import pandas as pd
import csv
import datetime

api_key = "RGAPI-63b038be-4f25-4929-9785-ce48e2ac25a7"

carac = ["!", "\"", "#", "$", "%", "&", "'", "(", ")", "*", "+", ",", "-", ".", "/", ":", ";", "<", "=", ">", "?", "@", "[", "\\", "]", "^", "_", "`", "{", "|", "}", "~"]

regionvalide = ["europe", "americas", "asia", "sea","esports"]

listnomtag = []
listregion = []
while True :
    riotid = input("Entrer le nom d'invocateur et le tag (séparé par le #): ").split("#")
    region = input("Entrer une région (europe, americas, asia, sea): ")

    assert region in regionvalide, "Erreur: Veuillez entrer une région valide."
    if len(riotid) == 2:
        assert len(riotid[0]) < 17 and len(riotid[0]) > 2, "Erreur: Le nom d'invocateur doit contenir entre 3 et 16 caractères."
        assert all(i not in carac for i in riotid[0]), "Erreur: Le nom d'invocateur ne doit pas contenir de caractères spéciaux."
        assert len(riotid[1]) < 6 and len(riotid[1]) > 2, "Erreur: Le tag doit contenir entre 3 et 5 caractères."
        name = riotid[0] + "/" + riotid[1]
        nameclean = name.replace(" ", "%20")
        listnomtag.append(nameclean)
        listregion.append(region)
    else:
        print("Erreur: Veuillez entrer un nom d'invocateur/tag valide.")
    continue_input = input("Voulez-vous ajouter un autre invocateur ? (o/n): ")
    if continue_input == "n":
        break
    else:
        continue
    

def get_puuid(name, region):
    listpuuid = []
    for i,k in zip(name, region):
        PUUID = f"https://{k}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{i}"
        PUUID = PUUID + "?api_key=" + api_key
        resPUUID = requests.get(PUUID)
        assert resPUUID.status_code == 200, resPUUID
        resPUUID = resPUUID.json()
        listpuuid.append(resPUUID['puuid'])
    return listpuuid


def get_matchlist(x,start,end,count):
    listmatchlist = []
    for i,k in zip(x,listregion):
        matchlist = f"https://{k}.api.riotgames.com/lol/match/v5/matches/by-puuid/{i}/ids?startTime={start}&endTime={end}&queue=420&type=ranked&start=0&count={count}"
        matchlist = matchlist + "&api_key=" + api_key
        resmatchlist = requests.get(matchlist)
        assert resmatchlist.status_code == 200, resmatchlist
        resmatchlist = resmatchlist.json()
        listmatchlist.append(resmatchlist)
    return listmatchlist

def vartab(x,id,region,nom):
    temp = []
    for i,k,j,m in zip(x,id,region,nom):
        for l in i:
            matchdata = f"https://{j}.api.riotgames.com/lol/match/v5/matches/{l}"
            matchdata = matchdata + "?api_key=" + api_key
            resmatchdata = requests.get(matchdata)
            assert resmatchdata.status_code == 200, resmatchdata
            resmatchdata = resmatchdata.json()
            witchindex = resmatchdata['metadata']['participants'].index(k)
            row = {"individual": m,
                    "date": datetime.datetime.fromtimestamp(resmatchdata['info']['gameEndTimestamp']/1000),
                    "champname": resmatchdata['info']['participants'][witchindex]['championName'],
                    "lane": resmatchdata['info']['participants'][witchindex]['lane'],
                    "mort": resmatchdata['info']['participants'][witchindex]['deaths'],
                    "kda": resmatchdata['info']['participants'][witchindex]['challenges']['kda'],
                    "dragkill": resmatchdata['info']['participants'][witchindex]['dragonKills'],
                    "baronkill": resmatchdata['info']['participants'][witchindex]['baronKills'],
                    "champdmg": resmatchdata['info']['participants'][witchindex]['totalDamageDealtToChampions'],
                    "dmgtaken": resmatchdata['info']['participants'][witchindex]['totalDamageTaken'],
                    "vision": resmatchdata['info']['participants'][witchindex]['visionScore'],
                    "dmgobj": resmatchdata['info']['participants'][witchindex]['damageDealtToObjectives'],
                    "goldspender": resmatchdata['info']['participants'][witchindex]['goldSpent'],
                    "goldearn": resmatchdata['info']['participants'][witchindex]['goldEarned'],
                    "Win": resmatchdata['info']['participants'][witchindex]['win'],
                    "bountyLevel": resmatchdata['info']['participants'][witchindex]['bountyLevel'],
                    "firstBloodKill": resmatchdata['info']['participants'][witchindex]['firstBloodKill'],
                    "inhibitorTakedowns": resmatchdata['info']['participants'][witchindex]['inhibitorTakedowns'],
                    "inhibitorsLost": resmatchdata['info']['participants'][witchindex]['inhibitorsLost'],
                    "killingSprees": resmatchdata['info']['participants'][witchindex]['killingSprees'],
                    "pentaKills": resmatchdata['info']['participants'][witchindex]['pentaKills'],
                    "quadraKills": resmatchdata['info']['participants'][witchindex]['quadraKills'],
                    "tripleKills": resmatchdata['info']['participants'][witchindex]['tripleKills'],
                    "teamElderDragonKills": resmatchdata['info']['participants'][witchindex]['challenges']["teamElderDragonKills"],
                    "teamBaronKills": resmatchdata['info']['participants'][witchindex]['challenges']["teamBaronKills"],
                    "turretsTakenWithRiftHerald": resmatchdata['info']['participants'][witchindex]['challenges']['turretsTakenWithRiftHerald'],
                    "teamRiftHeraldKills": resmatchdata['info']['participants'][witchindex]['challenges']['teamRiftHeraldKills'],
                    "lostAnInhibitor": resmatchdata['info']['participants'][witchindex]['challenges']['lostAnInhibitor'],
                    "acesBefore15Minutes": resmatchdata['info']['participants'][witchindex]['challenges']['acesBefore15Minutes'],
                    "voidMonsterKill": resmatchdata['info']['participants'][witchindex]['challenges']['voidMonsterKill'],
                    "goldPerMinute": resmatchdata['info']['participants'][witchindex]['challenges']['goldPerMinute'],}
            temp.append(row)
    pdfinal = pd.DataFrame(temp)
    return pdfinal

nbpartie = input("Entrer le nombre de parties à analyser: ")

assert nbpartie.isdigit(), "Erreur: Veuillez entrer un nombre entier."

puuid = get_puuid(listnomtag, listregion)

matchlist = get_matchlist(puuid, 1673308800,"", nbpartie)



data = vartab(matchlist, puuid, listregion, listnomtag)


data.to_csv("4.csv", index=False)

