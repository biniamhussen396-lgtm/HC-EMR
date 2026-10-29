def gregorian_to_jdn(year, month, day):
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    return day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045

def jdn_to_gregorian(jdn):
    import datetime
    a = jdn + 32044
    b = (4 * a + 3) // 146097
    c = a - (146097 * b) // 4
    d = (4 * c + 3) // 1461
    e = c - (1461 * d) // 4
    m = (5 * e + 2) // 153
    day = e - (153 * m + 2) // 5 + 1
    month = m + 3 - 12 * (m // 10)
    year = 100 * b + d - 4800 + (m // 10)
    return datetime.date(year, month, day)

JD_EPOCH_OFFSET_AMETE_MIHRET = 1723856

def ethiopian_to_jdn(year, month, day):
    return (JD_EPOCH_OFFSET_AMETE_MIHRET + 365) + 365 * (year - 1) + year // 4 + 30 * (month - 1) + day - 1

def eth_to_greg(year, month, day):
    jdn = ethiopian_to_jdn(year, month, day)
    return jdn_to_gregorian(jdn)

# Test 18 Tikimt 2019
g = eth_to_greg(2019, 2, 18)
print("18/02/2019 EC in Gregorian:", g, "Weekday (0=Mon, 6=Sun):", g.weekday())
g1 = eth_to_greg(2019, 2, 1)
print("01/02/2019 EC in Gregorian:", g1, "Weekday:", g1.weekday())
