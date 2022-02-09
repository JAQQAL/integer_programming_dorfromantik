name = 'ex_01'

tile_set = [
            [('gras', 0), ('gras', 0), ('gras', 0), ('gras', 0), ('gras', 0), ('gras', 0), ('gras', 0)],
            [('gras', 0), ('tree', 5), ('tree', 5), ('corn', 1), ('corn', 0), ('tree', 5), ('tree', 5)],
            [('gras', 0), ('gras', 0), ('gras', 0), ('tree', 6), ('tree', 6), ('tree', 5), ('gras', 0)],
            [('tree', 5), ('gras', 0), ('gras', 0), ('corn', 3), ('corn', 0), ('corn', 0), ('gras', 0)],
            [('house', 1), ('house', 1), ('house', 1), ('house', 1), ('house', 1), ('tree', 4), ('house', 2)],
            [('tree', 3), ('house', 1), ('tree', 4), ('house', 1), ('corn', 1), ('tree', 3), ('gras', 0)],
            [('house', 1), ('house', 1), ('house', 1), ('house', 1), ('house', 1), ('tree', 4), ('house', 2)],
            [('house', 1), ('gras', 0), ('corn', 1), ('corn', 0), ('gras', 0), ('gras', 0), ('gras', 0)],
            [('gras', 0), ('gras', 0), ('gras', 0), ('gras', 0), ('house', 1), ('gras', 0), ('gras', 0)],
            [('water', 0), ('house', 1), ('house', 1), ('water', 0), ('corn', 1), ('gras', 0), ('water', 1)],
            [('water', 0), ('water', 0), ('water', 0), ('tree', 6), ('tree', 6), ('tree', 5), ('water', 1)],
            [('water', 0), ('gras', 0), ('gras', 0), ('gras', 0), ('water', 0), ('gras', 0), ('water', 1)],#
            [('tree', 4), ('tree', 4), ('tree', 4), ('tree', 4), ('gras', 0), ('gras', 0), ('tree', 5)],#
            [('tree', 4), ('tree', 4), ('tree', 4), ('tree', 4), ('gras', 0), ('gras', 0), ('tree', 5)],#
            [('gras', 0), ('gras', 0), ('corn', 1), ('corn', 0), ('tree', 4), ('gras', 0), ('gras', 0)],#
            [('gras', 0), ('gras', 0), ('gras', 0), ('water', 0), ('gras', 0), ('water', 0), ('water', 1)],#
            [('gras', 0), ('gras', 0), ('gras', 0), ('tree', 5), ('tree', 5), ('house', 1), ('gras', 0)],#
            [('tree', 5), ('tree', 5), ('house', 1), ('gras', 0), ('tree', 5), ('gras', 0), ('tree', 5)],#
            [('gras', 0), ('tree', 4), ('gras', 0), ('water', 1), ('water', 0), ('gras', 0), ('gras', 0)],#
            [('house', 1), ('house', 1), ('gras', 0), ('gras', 0), ('water', 1), ('water', 0), ('gras', 0)],#
            [('tree', 5), ('tree', 5), ('gras', 0), ('gras', 0), ('tree', 5), ('gras', 0), ('tree', 5)],#
            [('house', 1), ('tree', 4), ('corn', 1), ('house', 1), ('gras', 0), ('corn', 1), ('gras', 0)],#
            [('rail', 0), ('gras', 0), ('gras', 0), ('rail', 0), ('gras', 0), ('gras', 0), ('rail', 1)],#
            [('house', 1), ('house', 1), ('corn', 1), ('tree', 4), ('gras', 0), ('gras', 0), ('gras', 0)],#
            [('water', 0), ('tree', 4), ('water', 0), ('tree', 6), ('tree', 6), ('tree', 5), ('water', 1)]
            ]

quests = { 1: (3, 4, '>', 'u'),
           3: (0, 21, '>', 'u')}