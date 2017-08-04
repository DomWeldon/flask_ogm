WITH [{
        unique_id: 1,
        name: 'Widget 1',
        colour: 'red'
    },
    {
        unique_id: 2,
        name: 'Widget 2',
        colour: 'red'
    },
    {
        unique_id: 3,
        name: 'Widget 3',
        colour: 'blue'
    }] AS widgets
UNWIND widgets as widget
CREATE (w:Widget)
SET w += widget
