$(function() {

    Morris.Area({
        element: 'morris-area-chart',
        data: [{
            period: '2010 Q1',
            Service: 2666,
            Change: null,
            Incidents: 2647
        }, {
            period: '2010 Q2',
            Service: 2778,
            Change: 2294,
            Incidents: 2441
        }, {
            period: '2010 Q3',
            Service: 4912,
            Change: 1969,
            Incidents: 2501
        }, {
            period: '2010 Q4',
            Service: 3767,
            Change: 3597,
            Incidents: 5689
        }, {
            period: '2011 Q1',
            Service: 6810,
            Change: 1914,
            Incidents: 2293
        }, {
            period: '2011 Q2',
            Service: 5670,
            Change: 4293,
            Incidents: 1881
        }, {
            period: '2011 Q3',
            Service: 4820,
            Change: 3795,
            Incidents: 1588
        }, {
            period: '2011 Q4',
            Service: 15073,
            Change: 5967,
            Incidents: 575
        }, {
            period: '2012 Q1',
            Service: 10687,
            Change: 4460,
            Incidents: 2028
        }, {
            period: '2012 Q2',
            Service: 8432,
            Change: 5713,
            Incidents: 1791
        }],
        xkey: 'period',
        ykeys: ['Incidents', 'Service', 'Change'],
        labels: ['Incidents', 'Change Request', 'Service Request'],
        pointSize: 2,
        hideHover: 'auto',
        resize: true,
        lineColors: ["#d9534f", "#337ab7", "#5cb85c", "#000000"]
    });

    Morris.Donut({
        element: 'morris-donut-chart',
        data: [{
            label: "Internal applications",
            value: 4
        }, {
            label: "External applications",
            value: 12
        }, {
            label: "Back End Systems",
            value: 7
        }],
        resize: true,
        colors: ["#5cb85c", "#d9534f", "#337ab7"]
    });

    // Morris.Bar({
    //     element: 'morris-bar-chart',
    //     data: [{
    //         y: '3326',
    //         p: 20,
    //         r: 20,
    //         c: 0
    //     }, {
    //         y: '3315',
    //         p: 30,
    //         r: 5,
    //         c: 25
    //     }, {
    //         y: '3128',
    //         p: 20,
    //         r: 0,
    //         c: 20
    //     }, {
    //         y: '3009',
    //         p: 5,
    //         r: 0,
    //         c: 5
    //     }, {
    //         y: '2995',
    //         p: 20,
    //         r: 2,
    //         c: 20
    //     }, {
    //         y: '2992',
    //         p: 50,
    //         r: 15,
    //         c: 45
    //     }, {
    //         y: '2765',
    //         p: 35,
    //         r: 0,
    //         c: 40
    //     }],
    //     xkey: 'y',
    //     ykeys: ['p', 'r', 'c'],
    //     labels: ['Planned effort', 'Remaining Effort', 'Completed Effort'],
    //     hideHover: 'auto',
    //     resize: true,
    //     xLabelAngle: 45
    // });
    
});
