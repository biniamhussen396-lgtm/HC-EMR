// Quick verification of Ethiopian calendar month start and days
function gregorianToJDN(year, month, day) {
    var a = Math.floor((14 - month) / 12);
    var y = year + 4800 - a;
    var m = month + 12 * a - 3;
    return day + Math.floor((153 * m + 2) / 5) + 365 * y +
        Math.floor(y / 4) - Math.floor(y / 100) + Math.floor(y / 400) - 32045;
}
function jdnToGregorian(jdn) {
    var a = jdn + 32044;
    var b = Math.floor((4 * a + 3) / 146097);
    var c = a - Math.floor((146097 * b) / 4);
    var d = Math.floor((4 * c + 3) / 1461);
    var e = c - Math.floor((1461 * d) / 4);
    var m = Math.floor((5 * e + 2) / 153);
    var day = e - Math.floor((153 * m + 2) / 5) + 1;
    var month = m + 3 - 12 * Math.floor(m / 10);
    var year = 100 * b + d - 4800 + Math.floor(m / 10);
    return new Date(year, month - 1, day);
}
var JD_EPOCH_OFFSET_AMETE_MIHRET = 1723856;
function ethiopianToJDN(year, month, day) {
    return (JD_EPOCH_OFFSET_AMETE_MIHRET + 365) +
        365 * (year - 1) +
        Math.floor(year / 4) +
        30 * (month - 1) +
        day - 1;
}
function ethToGreg(year, month, day) {
    var jdn = ethiopianToJDN(year, month, day);
    return jdnToGregorian(jdn);
}

// Today is 18 Tikimt 2019 EC
var g = ethToGreg(2019, 2, 18);
console.log("18/02/2019 EC in Gregorian:", g.toISOString());

// First day of Tikimt 2019 EC
var g1 = ethToGreg(2019, 2, 1);
console.log("01/02/2019 EC in Gregorian:", g1.toISOString(), "Weekday:", g1.getDay());
