'use strict';

/**
 * Ethiopian Calendar (EC) Localization and Conversion Service
 * Handles accurate Geez/Ethiopian date calculation, Amharic month naming,
 * and bi-directional conversion with the Gregorian Calendar.
 */
angular.module('bahmni.register')
    .factory('ethiopianCalendarService', ['$window', function ($window) {

        var amharicMonths = [
            "መስከረም", "ጥቅምት", "ኅዳር", "ታኅሣሥ", "ጥር", "የካቲት",
            "መጋቢት", "ሚያዝያ", "ግንቦት", "ሰኔ", "ሐምሌ", "ነሐሴ", "ጳጉሜ"
        ];

        var englishMonths = [
            "Meskerem", "Tikimt", "Hidar", "Tahsas", "Tir", "Yakatit",
            "Magabit", "Miyazya", "Ginbot", "Sene", "Hamle", "Nehase", "Pagume"
        ];

        var amharicDays = ["እሑድ", "ሰኞ", "ማክሰኞ", "ረቡዕ", "ሐሙስ", "ዓርብ", "ቅዳሜ"];

        // Ethiopian era starting JDN (August 29, 8 CE Julian = 1723856)
        var JD_EPOCH_OFFSET_AMETE_MIHRET = 1723856;

        /**
         * Convert Gregorian Date to Julian Day Number (JDN)
         */
        function gregorianToJDN(year, month, day) {
            var a = Math.floor((14 - month) / 12);
            var y = year + 4800 - a;
            var m = month + 12 * a - 3;
            return day + Math.floor((153 * m + 2) / 5) + 365 * y +
                Math.floor(y / 4) - Math.floor(y / 100) + Math.floor(y / 400) - 32045;
        }

        /**
         * Convert JDN to Gregorian Date (year, month, day)
         */
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
            return { year: year, month: month, day: day };
        }

        /**
         * Convert JDN to Ethiopian Date (year, month, day)
         */
        function jdnToEthiopian(jdn) {
            var r = (jdn - JD_EPOCH_OFFSET_AMETE_MIHRET) % 1461;
            var n = (r % 365) + 365 * Math.floor(r / 1460);
            var year = 4 * Math.floor((jdn - JD_EPOCH_OFFSET_AMETE_MIHRET) / 1461) +
                Math.floor(r / 365) - Math.floor(r / 1460);
            var month = Math.floor(n / 30) + 1;
            var day = (n % 30) + 1;
            return { year: year, month: month, day: day };
        }

        /**
         * Convert Ethiopian Date to JDN
         */
        function ethiopianToJDN(year, month, day) {
            return (JD_EPOCH_OFFSET_AMETE_MIHRET + 365) +
                365 * (year - 1) +
                Math.floor(year / 4) +
                30 * (month - 1) +
                day - 1;
        }

        /**
         * Convert JS Date or Gregorian string (YYYY-MM-DD) to Ethiopian Date object
         */
        function gregToEth(dateInput) {
            if (!dateInput) return null;
            var d;
            if (Array.isArray(dateInput)) {
                // Handle OpenMRS JSON date array [YYYY, MM, DD, HH, mm, ss]
                d = new Date(
                    dateInput[0],
                    (dateInput[1] || 1) - 1,
                    dateInput[2] || 1,
                    dateInput[3] || 0,
                    dateInput[4] || 0,
                    dateInput[5] || 0
                );
            } else if (dateInput instanceof Date) {
                d = dateInput;
            } else if (typeof dateInput === 'string') {
                // Remove time part if present
                var clean = dateInput.split('T')[0].split(' ')[0];
                var parts = clean.split('-');
                if (parts.length === 3) {
                    d = new Date(parseInt(parts[0], 10), parseInt(parts[1], 10) - 1, parseInt(parts[2], 10));
                } else {
                    d = new Date(dateInput);
                }
            } else {
                d = new Date(dateInput);
            }

            if (isNaN(d.getTime())) return null;

            // Try jQuery.calendars if available
            if ($window.jQuery && $window.jQuery.calendars) {
                try {
                    var gregCal = $window.jQuery.calendars.instance('gregorian');
                    var ethCal = $window.jQuery.calendars.instance('ethiopian');
                    var gregDate = gregCal.newDate(d.getFullYear(), d.getMonth() + 1, d.getDate());
                    var jd = gregCal.toJD(gregDate);
                    var ethDate = ethCal.fromJD(jd);
                    var ey = ethDate.year();
                    var em = ethDate.month();
                    var ed = ethDate.day();
                    return formatEthResult(ey, em, ed);
                } catch (e) {
                    // Fall back to pure math
                }
            }

            var jdn = gregorianToJDN(d.getFullYear(), d.getMonth() + 1, d.getDate());
            var eth = jdnToEthiopian(jdn);
            return formatEthResult(eth.year, eth.month, eth.day);
        }

        function formatEthResult(year, month, day) {
            var dd = day < 10 ? '0' + day : '' + day;
            var mm = month < 10 ? '0' + month : '' + month;
            var formatted = dd + '/' + mm + '/' + year;
            var amharicMonth = amharicMonths[month - 1] || '';
            var englishMonth = englishMonths[month - 1] || '';
            return {
                year: year,
                month: month,
                day: day,
                formatted: formatted,
                formattedFull: dd + ' ' + amharicMonth + ' ' + year + ' ዓ.ም',
                amharicMonth: amharicMonth,
                englishMonth: englishMonth
            };
        }

        /**
         * Convert Ethiopian Date string ("DD/MM/YYYY") to Gregorian Date
         */
        function ethToGreg(ethStr) {
            if (!ethStr || typeof ethStr !== 'string') return null;
            var parts = ethStr.trim().split('/');
            if (parts.length !== 3) {
                parts = ethStr.trim().split('-');
            }
            if (parts.length !== 3) return null;

            var day = parseInt(parts[0], 10);
            var month = parseInt(parts[1], 10);
            var year = parseInt(parts[2], 10);

            if (isNaN(day) || isNaN(month) || isNaN(year)) return null;

            // Try jQuery.calendars if available
            if ($window.jQuery && $window.jQuery.calendars) {
                try {
                    var ethCal = $window.jQuery.calendars.instance('ethiopian');
                    var gregCal = $window.jQuery.calendars.instance('gregorian');
                    var ethDate = ethCal.newDate(year, month, day);
                    var jd = ethCal.toJD(ethDate);
                    var gregDate = gregCal.fromJD(jd);
                    return new Date(gregDate.year(), gregDate.month() - 1, gregDate.day());
                } catch (e) {
                    // Fall back to pure math
                }
            }

            var jdn = ethiopianToJDN(year, month, day);
            var g = jdnToGregorian(jdn);
            return new Date(g.year, g.month - 1, g.day);
        }

        /**
         * Get current date in Ethiopian Calendar
         */
        function getCurrentEthDate() {
            return gregToEth(new Date());
        }

        /**
         * Quick date ranges in Ethiopian Calendar
         */
        function getPredefinedRanges() {
            var now = new Date();
            var ethNow = getCurrentEthDate();

            // Today range
            var todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0);
            var todayEnd = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59);

            // This week range (last 7 days)
            var weekStart = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
            weekStart.setHours(0, 0, 0, 0);

            // This Ethiopian Month (1st of current Eth month to end of current Eth month)
            var ethMonthStartGreg = ethToGreg('01/' + (ethNow.month < 10 ? '0' + ethNow.month : ethNow.month) + '/' + ethNow.year);
            var maxDay = ethNow.month === 13 ? (ethNow.year % 4 === 3 ? 6 : 5) : 30;
            var ethMonthEndGreg = ethToGreg(maxDay + '/' + (ethNow.month < 10 ? '0' + ethNow.month : ethNow.month) + '/' + ethNow.year);
            if (ethMonthEndGreg) ethMonthEndGreg.setHours(23, 59, 59, 999);

            return {
                all: { label: 'All Records', key: 'ALL', from: null, to: null },
                today: { label: 'Today (ዛሬ)', key: 'TODAY', from: todayStart, to: todayEnd, ethLabel: ethNow.formatted },
                thisWeek: { label: 'Past 7 Days', key: 'WEEK', from: weekStart, to: todayEnd },
                thisMonth: {
                    label: ethNow.amharicMonth + ' ' + ethNow.year + ' (This Month)',
                    key: 'MONTH',
                    from: ethMonthStartGreg,
                    to: ethMonthEndGreg,
                    ethMonth: ethNow.amharicMonth
                }
            };
        }

        return {
            amharicMonths: amharicMonths,
            englishMonths: englishMonths,
            amharicDays: amharicDays,
            gregToEth: gregToEth,
            ethToGreg: ethToGreg,
            getCurrentEthDate: getCurrentEthDate,
            getPredefinedRanges: getPredefinedRanges
        };
    }]);
