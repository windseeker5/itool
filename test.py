
# https://github.com/AnthonyBloomer/tmdbv3api

from tmdbv3api import TMDb, Movie, TV, Discover, Genre
import os, sys



tmdb = TMDb()
tmdb.api_key = 'da835367527db6ee192714cc83849e02'

tmdb.language = 'en'
tmdb.debug = True

#from tmdbv3api import Movie


print("")
print("__Popular Movie___________________________________")
print("")


genre = Genre()

genres = genre.movie_list()

print(genres)
print(type(genres))

for g in genres:
    print(g.id, g.name)


movie = Movie()
popular = movie.popular()


print('-----23-3-3-3-3-3--33333333333333333333333333-3-3-3--3-3-3-3-3-3-3-3-')
print(popular)
print(type(popular))
print('-----23-3-3-3-3-3--33333333333333333333333333-3-3-3--3-3-3-3-3-3-3-3-')


import json
import pandas as pd

# Assuming `obj` is your tmdbv3api.as_obj.AsObj object

# Convert to string using str()
#obj_str = str(popular)
obj_str = repr(popular)
# Convert to JSON string
#obj_json_str = json.dumps(popular)

print(obj_str)
#print(obj_json_str)


# Your nested JSON data
nested_json = {'page': 1, 'results': [{'adult': False, 'backdrop_path': '/pWsD91G2R1Da3AKM3ymr3UoIfRb.jpg', 'genre_ids': [28, 878, 18], 'id': 933131, 'original_language': 'ko', 'original_title': '황야', 'overview': 'After a deadly earthquake turns Seoul into a lawless badland, a fearless huntsman springs into action to rescue a teenager abducted by a mad doctor.', 'popularity': 2428.936, 'poster_path': '/zVMyvNowgbsBAL6O6esWfRpAcOb.jpg', 'release_date': '2024-01-26', 'title': 'Badland Hunters', 'video': False, 'vote_average': 6.805, 'vote_count': 254}, {'adult': False, 'backdrop_path': '/4MCKNAc6AbWjEsM2h9Xc29owo4z.jpg', 'genre_ids': [28, 53, 18], 'id': 866398, 'original_language': 'en', 'original_title': 'The Beekeeper', 'overview': 'One man’s campaign for vengeance takes on national stakes after he is revealed to be a former operative of a powerful and clandestine organization known as Beekeepers.', 'popularity': 2265.436, 'poster_path': '/A7EByudX0eOzlkQ2FIbogzyazm2.jpg', 'release_date': '2024-01-10', 'title': 'The Beekeeper', 'video': False, 'vote_average': 7.273, 'vote_count': 916}, {'adult': False, 'backdrop_path': '/unvtbkgxh47BewQ8pENvdOdme0r.jpg', 'genre_ids': [28, 18], 'id': 1212073, 'original_language': 'de', 'original_title': '60 Minuten', 'overview': 'Desperate to keep custody of his daughter, a mixed martial arts fighter abandons a big match and races across Berlin to attend her birthday party.', 'popularity': 1346.069, 'poster_path': '/jojfbnIHGsRpodIood3OQoqA45Y.jpg', 'release_date': '2024-01-19', 'title': 'Sixty Minutes', 'video': False, 'vote_average': 6.983, 'vote_count': 239}, {'adult': False, 'backdrop_path': '/yyFc8Iclt2jxPmLztbP617xXllT.jpg', 'genre_ids': [35, 10751, 14], 'id': 787699, 'original_language': 'en', 'original_title': 'Wonka', 'overview': 'Willy Wonka – chock-full of ideas and determined to change the world one delectable bite at a time – is proof that the best things in life begin with a dream, and if you’re lucky enough to meet Willy Wonka, anything is possible.', 'popularity': 1303.308, 'poster_path': '/qhb1qOilapbapxWQn9jtRCMwXJF.jpg', 'release_date': '2023-12-06', 'title': 'Wonka', 'video': False, 'vote_average': 7.2, 'vote_count': 1974}, {'adult': False, 'backdrop_path': '/criPrxkTggCra1jch49jsiSeXo1.jpg', 'genre_ids': [878, 12, 28], 'id': 609681, 'original_language': 'en', 'original_title': 'The Marvels', 'overview': 'Carol Danvers, aka Captain Marvel, has reclaimed her identity from the tyrannical Kree and taken revenge on the Supreme Intelligence. But unintended consequences see Carol shouldering the burden of a destabilized universe. When her duties send her to an anomalous wormhole linked to a Kree revolutionary, her powers become entangled with that of Jersey City super-fan Kamala Khan, aka Ms. Marvel, and Carol’s estranged niece, now S.A.B.E.R. astronaut Captain Monica Rambeau. Together, this unlikely trio must team up and learn to work in concert to save the universe.', 'popularity': 1287.814, 'poster_path': '/9GBhzXMFjgcZ3FdR9w3bUMMTps5.jpg', 'release_date': '2023-11-08', 'title': 'The Marvels', 'video': False, 'vote_average': 6.335, 'vote_count': 1510}, {'adult': False, 'backdrop_path': '/cnqwv5Uz3UW5f086IWbQKr3ksJr.jpg', 'genre_ids': [28, 12, 14], 'id': 572802, 'original_language': 'en', 'original_title': 'Aquaman and the Lost Kingdom', 'overview': "Black Manta seeks revenge on Aquaman for his father's death. Wielding the Black Trident's power, he becomes a formidable foe. To defend Atlantis, Aquaman forges an alliance with his imprisoned brother. They must protect the kingdom.", 'popularity': 970.392, 'poster_path': '/7lTnXOy0iNtBAdRP3TZvaKJ77F6.jpg', 'release_date': '2023-12-20', 'title': 'Aquaman and the Lost Kingdom', 'video': False, 'vote_average': 6.932, 'vote_count': 1528}, {'adult': False, 'backdrop_path': '/meyhnvssZOPPjud4F1CjOb4snET.jpg', 'genre_ids': [16, 28, 12, 35, 10751], 'id': 940551, 'original_language': 'en', 'original_title': 'Migration', 'overview': 'After a migrating duck family alights on their pond with thrilling tales of far-flung places, the Mallard family embarks on a family road trip, from New England, to New York City, to tropical Jamaica.', 'popularity': 961.294, 'poster_path': '/ldfCF9RhR40mppkzmftxapaHeTo.jpg', 'release_date': '2023-12-06', 'title': 'Migration', 'video': False, 'vote_average': 7.647, 'vote_count': 573}, {'adult': False, 'backdrop_path': '/ehumsuIBbgAe1hg343oszCLrAfI.jpg', 'genre_ids': [16, 10751, 14, 12], 'id': 1022796, 'original_language': 'en', 'original_title': 'Wish', 'overview': 'Asha, a sharp-witted idealist, makes a wish so powerful that it is answered by a cosmic force – a little ball of boundless energy called Star. Together, Asha and Star confront a most formidable foe - the ruler of Rosas, King Magnifico - to save her community and prove that when the will of one courageous human connects with the magic of the stars, wondrous things can happen.', 'popularity': 944.601, 'poster_path': '/AcoVfiv1rrWOmAdpnAMnM56ki19.jpg', 'release_date': '2023-11-13', 'title': 'Wish', 'video': False, 'vote_average': 6.653, 'vote_count': 670}, {'adult': False, 'backdrop_path': '/rz8GGX5Id2hCW1KzAIY4xwbQw1w.jpg', 'genre_ids': [28, 35, 80], 'id': 955916, 'original_language': 'en', 'original_title': 'Lift', 'overview': 'An international heist crew, led by Cyrus Whitaker, race to lift $500 million in gold from a passenger plane at 40,000 feet.', 'popularity': 926.968, 'poster_path': '/46sp1Z9b2PPTgCMyA87g9aTLUXi.jpg', 'release_date': '2024-01-10', 'title': 'Lift', 'video': False, 'vote_average': 6.581, 'vote_count': 714}, {'adult': False, 'backdrop_path': '/zLj0peaxy5y2SlC6wNIQ4V0pfqg.jpg', 'genre_ids': [16, 10751, 35, 14], 'id': 1139829, 'original_language': 'en', 'original_title': 'Orion and the Dark', 'overview': 'A boy with an active imagination faces his fears on an unforgettable journey through the night with his new friend: a giant, smiling creature named Dark.', 'popularity': 836.851, 'poster_path': '/uHiXFLMlnl5jBjtfOliapN16yBD.jpg', 'release_date': '2024-02-02', 'title': 'Orion and the Dark', 'video': False, 'vote_average': 6.778, 'vote_count': 126}, {'adult': False, 'backdrop_path': '/nTPFkLUARmo1bYHfkfdNpRKgEOs.jpg', 'genre_ids': [35, 10749], 'id': 1072790, 'original_language': 'en', 'original_title': 'Anyone But You', 'overview': 'Bea and Ben look like the perfect couple, but after an amazing first date something happens that turns their fiery hot attraction ice cold - until they find themselves unexpectedly thrust together at a destination wedding in Australia. So they do what any two mature adults would do: pretend to be a couple.', 'popularity': 725.952, 'poster_path': '/yRt7MGBElkLQOYRvLTT1b3B1rcp.jpg', 'release_date': '2023-12-21', 'title': 'Anyone But You', 'video': False, 'vote_average': 7.22, 'vote_count': 279}, {'adult': False, 'backdrop_path': '/f1AQhx6ZfGhPZFTVKgxG91PhEYc.jpg', 'genre_ids': [36, 10752, 28, 18], 'id': 753342, 'original_language': 'en', 'original_title': 'Napoleon', 'overview': 'An epic that details the checkered rise and fall of French Emperor Napoleon Bonaparte and his relentless journey to power through the prism of his addictive, volatile relationship with his wife, Josephine.', 'popularity': 652.558, 'poster_path': '/vcZWJGvB5xydWuUO1vaTLI82tGi.jpg', 'release_date': '2023-11-22', 'title': 'Napoleon', 'video': False, 'vote_average': 6.525, 'vote_count': 1627}, {'adult': False, 'backdrop_path': '/8GnWDLn2AhnmkQ7hlQ9NJUYobSS.jpg', 'genre_ids': [18, 878, 28], 'id': 695721, 'original_language': 'en', 'original_title': 'The Hunger Games: The Ballad of Songbirds & Snakes', 'overview': '64 years before he becomes the tyrannical president of Panem, Coriolanus Snow sees a chance for a change in fortunes when he mentors Lucy Gray Baird, the female tribute from District 12.', 'popularity': 652.036, 'poster_path': '/mBaXZ95R2OxueZhvQbcEWy2DqyO.jpg', 'release_date': '2023-11-15', 'title': 'The Hunger Games: The Ballad of Songbirds & Snakes', 'video': False, 'vote_average': 7.223, 'vote_count': 1679}, {'adult': False, 'backdrop_path': '/yl2GfeCaPoxChcGyM5p7vYp1CKS.jpg', 'genre_ids': [28, 35, 10749], 'id': 848187, 'original_language': 'en', 'original_title': 'Role Play', 'overview': 'Emma has a wonderful husband and two kids in the suburbs of New Jersey – she also has a secret life as an assassin for hire – a secret that her husband David discovers when the couple decide to spice up their marriage with a little role play.', 'popularity': 611.977, 'poster_path': '/7MhXiTmTl16LwXNPbWCmqxj7UxH.jpg', 'release_date': '2024-01-04', 'title': 'Role Play', 'video': False, 'vote_average': 6.036, 'vote_count': 293}, {'adult': False, 'backdrop_path': '/acpFrSmVLnTNAIuHxnZArkC3dwU.jpg', 'genre_ids': [16, 28, 12, 10751, 14], 'id': 598387, 'original_language': 'en', 'original_title': "The Tiger's Apprentice", 'overview': 'After the death of his grandmother, Tom Lee discovers he is part of a long lineage of magical protectors known as the Guardians. With guidance from a mythical tiger named Hu and the other Zodiac animal warriors, Tom trains to take on an evil force that threatens humanity.', 'popularity': 598.595, 'poster_path': '/iiid1xMhoAcW83VJ9LdAqf4Vtbr.jpg', 'release_date': '2024-02-02', 'title': "The Tiger's Apprentice", 'video': False, 'vote_average': 6.9, 'vote_count': 32}, {'adult': False, 'backdrop_path': '/1BFLsVxE1NzCIwicfOPtzzB4Kxh.jpg', 'genre_ids': [80, 53, 28], 'id': 982940, 'original_language': 'en', 'original_title': 'Due Justice', 'overview': 'An attorney with a military past hunts down the gang who killed his wife and took his daughter.', 'popularity': 592.782, 'poster_path': '/35Uef7fz9ctYbJLXbJBCqvtttEQ.jpg', 'release_date': '2023-11-24', 'title': 'Due Justice', 'video': False, 'vote_average': 6.778, 'vote_count': 27}, {'adult': False, 'backdrop_path': '/6OnoMgGFuZ921eV8v8yEyXoag19.jpg', 'genre_ids': [28, 53], 'id': 1211957, 'original_language': 'en', 'original_title': 'The Painter', 'overview': 'An ex-CIA operative is thrown back into a dangerous world when a mysterious woman from his past resurfaces. Now exposed and targeted by a relentless killer and a rogue black ops program, he must rely on skills he thought he left behind in a high-stakes game of survival.', 'popularity': 590.359, 'poster_path': '/UZ0ydgbXtnrq8xZCI5lHVXVcH9.jpg', 'release_date': '2024-01-05', 'title': 'The Painter', 'video': False, 'vote_average': 7.1, 'vote_count': 51}, {'adult': False, 'backdrop_path': '/lVoHnqwfkDv4GHktEewBguhiNRn.jpg', 'genre_ids': [53, 28, 18], 'id': 1183905, 'original_language': 'de', 'original_title': 'Trunk - Locked In', 'overview': 'Malina wakes up disoriented in the trunk of a speeding car and discovers to her horror that she is missing more than her memory. With her mobile phone as the only link to the outside world, she wages a desperate battle for survival.', 'popularity': 562.734, 'poster_path': '/5KYOsr338jGBXfmdUT1prj4ZZW4.jpg', 'release_date': '2023-11-24', 'title': 'Trunk: Locked In', 'video': False, 'vote_average': 5.571, 'vote_count': 28}, {'adult': False, 'backdrop_path': '/r9oTasGQofvkQY5vlUXglneF64Z.jpg', 'genre_ids': [28, 35], 'id': 1029575, 'original_language': 'en', 'original_title': 'The Family Plan', 'overview': "Dan Morgan is many things: a devoted husband, a loving father, a celebrated car salesman. He's also a former assassin. And when his past catches up to his present, he's forced to take his unsuspecting family on a road trip unlike any other.", 'popularity': 525.748, 'poster_path': '/aftI2czRi5nFXt9FCaXJOX4SRvO.jpg', 'release_date': '2024-02-02', 'title': 'The Family Plan', 'video': False, 'vote_average': 5.809, 'vote_count': 97}, {'adult': False, 'backdrop_path': '/swQYMwoF9GBevc9lEdTz7v9v8Wb.jpg', 'genre_ids': [28, 12, 14], 'id': 725870, 'original_language': 'en', 'original_title': 'Indiana Jones 5', 'overview': 'The plot is unknown at this time.', 'popularity': 502.45, 'poster_path': '/5rKGMG2bVmNHE7BnAvbrWn3oJTq.jpg', 'release_date': '2023-11-22', 'title': 'Indiana Jones 5', 'video': False, 'vote_average': 0, 'vote_count': 0}, {'adult': False, 'backdrop_path': '/iDdpiUnCeXvBmrkbf7OYmJzvRvS.jpg', 'genre_ids': [28, 12, 18], 'id': 941447, 'original_language': 'en', 'original_title': 'The Contractor', 'overview': "When a professional thief witnesses a horrific crime involving a U.S. senator, he's determined to expose the truth, putting both his life and the lives of those he loves in danger. But the senator has a secret weapon - Blake's best friend and lover, CIA agent Angela Todd, who is tasked with keeping Blake out of harm's way.", 'popularity': 484.444, 'poster_path': '/rEzAjCEfhaX9mAN2I6Myp2D5QYb.jpg', 'release_date': '2023-12-01', 'title': 'The Contractor', 'video': False, 'vote_average': 7.656, 'vote_count': 136}, {'adult': False, 'backdrop_path': '/ofZkrd0lkUPhm8sqkt7XbpaKX0P.jpg', 'genre_ids': [53, 80], 'id': 1096701, 'original_language': 'en', 'original_title': 'Last Words', 'overview': 'A world-renowned novelist is on a deadline for his next book, so his publisher sends him to a remote village in the Alps to cure his writer’s block. Before leaving for the mountain, the novelist’s wife gives him an antique typewriter as a gift. Once at the village, the writer discovers that the typewriter has the power to predict death, and he must do everything in his power to stop it before it’s too late.', 'popularity': 468.748, 'poster_path': '/ytwl6ogZNfgjlfoewaXXdAkmwGV.jpg', 'release_date': '2023-11-24', 'title': 'Last Words', 'video': False, 'vote_average': 6.9, 'vote_count': 111}, {'adult': False, 'backdrop_path': '/t2wRf1YVDN1VvcKx5BDlsL1dYbX.jpg', 'genre_ids': [28, 53], 'id': 855105, 'original_language': 'en', 'original_title': 'Bullet Train', 'overview': 'Five assassins aboard a fast moving bullet train find out their missions have something in common.', 'popularity': 426.399, 'poster_path': '/4nQhz0nR0blIDvobYxj6b4ZQAZy.jpg', 'release_date': '2023-12-15', 'title': 'Bullet Train', 'video': False, 'vote_average': 5.875, 'vote_count': 112}, {'adult': False, 'backdrop_path': '/fIcrwLOXJoZuYcbzt25s3L3A5S2.jpg', 'genre_ids': [28, 80, 53], 'id': 861571, 'original_language': 'en', 'original_title': 'Deadlock', 'overview': 'When a marine’s undercover narcotics sting is exposed and he is kidnapped by the ruthless cartel he was targeting, he must devise an escape plan against impossible odds to survive.', 'popularity': 421.529, 'poster_path': '/5wVxd0F2cKvdVSgvcl4C76pyD3R.jpg', 'release_date': '2024-01-05', 'title': 'Deadlock', 'video': False, 'vote_average': 5.9, 'vote_count': 57}], 'total_pages': 500, 'total_results': 10000}

# Flatten the nested JSON
df = pd.json_normalize(nested_json, 'results')


print("")
print("////////////////////////////////////////////////////")
print("")



print(obj_str)
print(type(obj_str))

json_object = json.loads(obj_str)

sys.exit()

df = pd.json_normalize(json_object, 'results')


# Display the DataFrame
print(df)

print("")
print("////////////////////////////////////////////////////")
print("")
sys.exit()

"""
for p in popular:
    print("p:",p)
    print(p.id)
    print(p.title)
    print(p.release_date)
    print(p.popularity)
    print(p.vote_average)
    print(p.vote_count)
    # print(p.overview)
    # print(p.poster_path)


'backdrop_path': '/r9oTasGQofvkQY5vlUXglneF64Z.jpg', 
 'poster_path': '/a6syn9qcU4a54Lmi3JoIr1XvhFU.jpg', 

'genre_ids': [28, 35], 
'id': 1029575, 
'original_language': 'en',
 'original_title': 'The Family Plan', 


 
 'popularity': 525.748, 
 'release_date': '2023-12-14', 
 'title': 'The Family Plan', 
 'video': False, 
 'vote_average': 7.354, 
 'vote_count': 865}


"""




search = movie.search('Mad Max')

print(search)
print(type(search))


print("")
print("_____________________________________")
print("")

"""
for res in search:
    print(res.id)
    print(res.title)
    print(res.overview)
    print(res.poster_path)
    print(res.vote_average)
"""
tv = TV()
show = tv.search('Breaking Bad')

for result in show:
    print(result.name)
    print(result.overview)


print("")
print("___Discover_by_date__________________________________")
print("")



# What movies are in theatres?

discover = Discover()
movie = discover.discover_movies({
    'primary_release_date.gte': '2023-11-01',
    'primary_release_date.lte': '2024-02-10'
})

print(movie)
print(type(movie))

print("")
print("___Discover_by_popularity_____________________________")
print("")


# What are the most popular movies?

movie = discover.discover_movies({
    'sort_by': 'popularity.desc'
})

print(movie)
print(type(movie))

# What are the most popular kids movies?

movie = discover.discover_movies({
    'certification_country': 'US',
    'certification.lte': 'G',
    'sort_by': 'popularity.desc'
})




# What are the most popular TV shows?

show = discover.discover_tv_shows({
    'sort_by': 'popularity.desc'
})

# What are the best dramas?

print("")
print("___Discover_Show_by_filters______________________")
print("")



show = discover.discover_tv_shows({
    'with_genres': 18,
    'sort_by': 'vote_average.desc',
    'vote_average.gte': 10,
    'popularity.gte': 2,
    'vote_count.gte': 100
})


print(show)
print(type(show))

