from tzwhere import tzwhere
TZ = tzwhere.tzwhere()

NAME_TO_ID = {  # bill_ab.heap.gis_gkh_time_zone_olson_id
    'Unknown': 0,
    'Europe/Kaliningrad': 1, 'Europe/Moscow': 2, 'Europe/Simferopol': 3,
    'Europe/Volgograd': 4, 'Europe/Samara': 5, 'Asia/Yekaterinburg': 6,
    'Asia/Novosibirsk': 7, 'Asia/Omsk': 8, 'Asia/Krasnoyarsk': 9,
    'Asia/Novokuznetsk': 10, 'Asia/Irkutsk': 11, 'Asia/Chita': 12,
    'Asia/Yakutsk': 13, 'Asia/Khandyga': 14, 'Asia/Vladivostok': 15,
    'Asia/Magadan': 16, 'Asia/Sakhalin': 17, 'Asia/Ust-Nera': 18,
    'Asia/Srednekolymsk': 19, 'Asia/Kamchatka': 20, 'Asia/Anadyr': 21
}


def get_id(point):
    unknown = NAME_TO_ID['Unknown']
    if not point:
        return unknown
    if point.get('_type') != 'point':
        return unknown
    coordinates = point.get('coordinates')
    if not coordinates:
        return unknown
    name = TZ.tzNameAt(latitude=coordinates[1], longitude=coordinates[0])
    return NAME_TO_ID.get(name, unknown)
