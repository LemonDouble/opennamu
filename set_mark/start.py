from . import tool

import re

def table_parser(data, cel_data, start_data, num = 0):
    table_class = 'class="'
    all_table = 'style="'
    cel_style = 'style="'
    row_style = 'style="'
    row = ''
    cel = ''

    table_width = re.search("<table ?width=((?:(?!>).)*)>", data)
    if table_width:
        all_table += 'width: ' + table_width.groups()[0] + ';'
    
    table_height = re.search("<table ?height=((?:(?!>).)*)>", data)
    if table_height:
        all_table += 'height: ' + table_height.groups()[0] + ';'
    
    table_align = re.search("<table ?align=((?:(?!>).)*)>", data)
    if table_align:
        if table_align.groups()[0] == 'right':
            all_table += 'float: right;'
        elif table_align.groups()[0] == 'center':
            all_table += 'margin: auto;'
            
    table_text_align = re.search("<table ?textalign=((?:(?!>).)*)>", data)
    if table_text_align:
        num = 1
        if table_text_align.groups()[0] == 'right':
            all_table += 'text-align: right;'
        elif table_text_align.groups()[0] == 'center':
            all_table += 'text-align: center;'

    row_t_a = re.search("<row ?textalign=((?:(?!>).)*)>", data)
    if row_t_a:
        if row_t_a.groups()[0] == 'right':
            row_style += 'text-align: right;'
        elif row_t_a.groups()[0] == 'center':
            row_style += 'text-align: center;'
        else:
            row_style += 'text-align: left;'
    
    table_cel = re.search("<-((?:(?!>).)*)>", data)
    if table_cel:
        cel = 'colspan="' + table_cel.groups()[0] + '"'
    else:
        cel = 'colspan="' + str(round(len(start_data) / 2)) + '"'   

    table_row = re.search("<\|((?:(?!>).)*)>", data)
    if table_row:
        row = 'rowspan="' + table_row.groups()[0] + '"'

    row_bgcolor = re.search("<rowbgcolor=(#(?:[0-9a-f-A-F]{3}){1,2}|\w+)>", data)
    if row_bgcolor:
        row_style += 'background: ' + row_bgcolor.groups()[0] + ';'
        
    table_border = re.search("<table ?bordercolor=(#(?:[0-9a-f-A-F]{3}){1,2}|\w+)>", data)
    if table_border:
        all_table += 'border: ' + table_border.groups()[0] + ' 2px solid;'
        
    table_bgcolor = re.search("<table ?bgcolor=(#(?:[0-9a-f-A-F]{3}){1,2}|\w+)>", data)
    if table_bgcolor:
        all_table += 'background: ' + table_bgcolor.groups()[0] + ';'
        
    bgcolor = re.search("<(?:bgcolor=)?(#(?:[0-9a-f-A-F]{3}){1,2}|\w+)>", data)
    if bgcolor:
        cel_style += 'background: ' + bgcolor.groups()[0] + ';'
        
    cel_width = re.search("<width=((?:(?!>).)*)>", data)
    if cel_width:
        cel_style += 'width: ' + cel_width.groups()[0] + ';'

    cel_height = re.search("<height=((?:(?!>).)*)>", data)
    if cel_height:
        cel_style += 'height: ' + cel_height.groups()[0] + ';'
        
    text_right = re.search("<\)>", data)
    text_center = re.search("<:>", data)
    text_left = re.search("<\(>",  data)
    if text_right:
        cel_style += 'text-align: right;'
    elif text_center:
        cel_style += 'text-align: center;'
    elif text_left:
        cel_style += 'text-align: left;'
    elif num == 0:
        if re.search('^ (.*) $', cel_data):
            cel_style += 'text-align: center;'
        elif re.search('^ (.*)$', cel_data):
            cel_style += 'text-align: right;'
        elif re.search('^(.*) $', cel_data):
            cel_style += 'text-align: left;'

    text_class = re.search("<table ?class=((?:(?!>).)+)>", data)
    if text_class:
        table_class += text_class.groups()[0]
        
    all_table += '"'
    cel_style += '"'
    row_style += '"'
    table_class += '"'

    return [all_table, row_style, cel_style, row, cel, table_class, num]

def start(conn, data, title):
    # DB 지정
    curs = conn.cursor()

    # 맨 앞과 끝에 개행 문자 추가
    data = '\r\n' + data + '\r\n'

    while 1:
        include = re.search('\[include\(((?:(?!\)\]).)+)\)\]', data)
        if include:
            include = include.groups()[0]

            curs.execute("select data from data where title = ?", [include])
            include_data = curs.fetchall()
            if include_data:
                data = re.sub('\[include\(((?:(?!\)\]).)+)\)\]', '\r\n' + include_data[0][0] + '\r\n', data, 1)
            else:
                data = re.sub('\[include\(((?:(?!\)\]).)+)\)\]', '[[' + include + ']]', data, 1)
        else:
            break

    # 텍스트 꾸미기 문법
    data = re.sub('\'\'\'(?P<in>(?:(?!\'\'\').)+)\'\'\'', '<b>\g<in></b>', data)
    data = re.sub('\'\'(?P<in>(?:(?!\'\').)+)\'\'', '<i>\g<in></i>', data)

    data = re.sub('~~(?P<in>(?:(?!~~).)+)~~', '<s>\g<in></s>', data)
    data = re.sub('--(?P<in>(?:(?!~~).)+)--', '<s>\g<in></s>', data)

    data = re.sub('__(?P<in>(?:(?!__).)+)__', '<u>\g<in></u>', data)
    
    data = re.sub('^^(?P<in>(?:(?!^^).)+)^^', '<sup>\g<in></sup>', data)
    data = re.sub(',,(?P<in>(?:(?!,,).)+),,', '<sub>\g<in></sub>', data)

    # 넘겨주기 변환
    data = re.sub('\r\n#(?:redirect|넘겨주기) (?P<in>(?:(?!\r\n).)+)\r\n', '<meta http-equiv="refresh" content="0; url=/w/\g<in>?froms=' + tool.url_pas(title) + '">', data)

    # [목차(없음)] 처리
    if not re.search('\[목차\(없음\)\]\r\n', data):
        if not re.search('\[목차\]', data):
            data = re.sub('\r\n(?P<in>={1,6}) ?(?P<out>(?:(?!=).)+) ?={1,6}\r\n', '\r\n[목차]\r\n\g<in> \g<out> \g<in>\r\n', data, 1)
    else:
        data = re.sub('\[목차\(없음\)\]\r\n', '', data)

    # 문단 문법
    toc_full = 0
    toc_top_stack = 6
    toc_stack = [0, 0, 0, 0, 0, 0]
    toc_data = '<div id="toc"><span style="font-size: 18px;">목차</span>\r\n\r\n'
    while 1:
        toc = re.search('\r\n(={1,6}) ?((?:(?!=).)+) ?={1,6}\r\n', data)
        if toc:
            toc = toc.groups()
            toc_number = len(toc[0])

            # 더 크면 그 전 스택은 초기화
            if toc_full > toc_number:
                for i in range(toc_number, 6):
                    toc_stack[i] = 0

            if toc_top_stack > toc_number:
                toc_top_stack = toc_number
                    
            toc_full = toc_number        
            toc_stack[toc_number - 1] += 1
            toc_number = str(toc_number)
            all_stack = ''

            # 스택 합치기
            for i in range(0, 6):
                all_stack += str(toc_stack[i]) + '.'

            all_stack = re.sub('0.', '', all_stack)
            
            data = re.sub('\r\n(={1,6}) ?((?:(?!=).)+) ?={1,6}\r\n', '\r\n<h' + toc_number + '><a href="">' + all_stack + '</a> ' + toc[1] + '</h' + toc_number + '><hr id="under_bar" style="margin-top: -5px; margin-bottom: 10px;">\r\n', data, 1)
            toc_data += '<span style="margin-left: ' + str((toc_full - toc_top_stack) * 10) + 'px"><a href="">' + all_stack + '</a> ' + toc[1] + '</span>\r\n'
        else:
            break

    toc_data += '</div>'
    
    data = re.sub('\[목차\]', toc_data, data)

    while 1:
        hr = re.search('\r\n-{4,9}\r\n', data)
        if hr:
            data = re.sub('\r\n-{4,9}\r\n', '<hr>', data, 1)
        else:
            break

    # 리스트 구현
    while 1:
        li = re.search('(\r\n(?:(?: *)\* ?(?:(?:(?!\r\n).)+)\r\n)+)', data)
        if li:
            li = li.groups()[0]

            while 1:
                sub_li = re.search('\r\n(?:( *)\* ?((?:(?!\r\n).)+))', li)
                if sub_li:
                    sub_li = sub_li.groups()

                    # 앞의 공백 만큼 margin 먹임
                    if len(sub_li[0]) == 0:
                        margin = 20
                    else:
                        margin = len(sub_li[0]) * 20

                    li = re.sub('\r\n(?:( *)\* ?((?:(?!\r\n).)+))', '<li style="margin-left: ' + str(margin) + 'px">' + sub_li[1] + '</li>', li, 1)
                else:
                    break

            data = re.sub('(\r\n(?:(?: *)\* ?(?:(?:(?!\r\n).)+)\r\n)+)', '<ul>' + li + '</ul>\r\n', data, 1)
        else:
            break

    # 들여쓰기 구현
    while 1:
        indent = re.search('\r\n( +)', data)
        if indent:
            indent = len(indent.groups()[0])
            
            # 앞에 공백 만큼 margin 먹임
            margin = '<span style="margin-left: 20px;"></span>' * indent

            data = re.sub('\r\n( +)', '\r\n' + margin, data, 1)
        else:
            break

    # 표 처리
    while 1:
        table = re.search('((?:(?:(?:(?:\|\|)+(?:(?:(?!\|\|).(?:\r\n)*)+))+)\|\|(?:\r\n)?)+)', data)
        if table:
            table = table.groups()[0]
            
            # return [all_table, row_style, cel_style, row, cel, table_class, num]
            while 1:
                all_table = re.search('^((?:\|\|)+)((?:<(?:(?:(?!>).)+)>)*)((?:(?!\|\||<\/td>).)+)', table)
                if all_table:
                    all_table = all_table.groups()

                    return_table = table_parser(all_table[1], all_table[2], all_table[0])
                    number = return_table[6]

                    table = re.sub('^\|\|((?:<(?:(?:(?!>).)+)>)*)', '<table ' + return_table[5] + ' ' + return_table[0] + '><tbody><tr ' + return_table[1] + '><td ' + return_table[2] + ' ' + return_table[3] + ' ' + return_table[4] + '>', table, 1)
                else:
                    break

            table = re.sub('\|\|\r\n$', '</td></tr></tbody></table>', table)

            while 1:
                row_table = re.search('\|\|\r\n((?:\|\|)+)((?:<(?:(?:(?!>).)+)>)*)((?:(?!\|\||<\/td>).)+)', table)
                if row_table:
                    row_table = row_table.groups()

                    return_table = table_parser(row_table[1], row_table[2], row_table[0], number)

                    table = re.sub('\|\|\r\n((?:\|\|)+)((?:<(?:(?:(?!>).)+)>)*)', '</td></tr><tr ' + return_table[1] + '><td ' + return_table[2] + ' ' + return_table[3] + ' ' + return_table[4] + '>', table, 1)
                else:
                    break

            while 1:
                cel_table = re.search('((?:\|\|)+)((?:<(?:(?:(?!>).)+)>)*)((?:(?!\|\||<\/td>).)+)', table)
                if cel_table:
                    cel_table = cel_table.groups()

                    return_table = table_parser(cel_table[1], cel_table[2], cel_table[0], number)

                    table = re.sub('((?:\|\|)+)((?:<(?:(?:(?!>).)+)>)*)', '</td><td ' + return_table[2] + ' ' + return_table[3] + ' ' + return_table[4] + '>', table, 1)
                else:
                    break

            data = re.sub('((?:(?:(?:(?:\|\|)+(?:(?:(?!\|\|).(?:\r\n)*)+))+)\|\|(?:\r\n)?)+)', table, data, 1)
        else:
            break

    while 1:
        link = re.search('\[\[((?:(?!\]\]).)+)\]\]', data)
        if link:
            link = link.groups()[0]

            link_split = re.search('((?:(?!\|).)+)(?:\|((?:(?!\|).)+))', link)
            if link_split:
                link_split = link_split.groups()

                main_link = link_split[0]
                see_link = link_split[1]
            else:
                main_link = link
                see_link = link

            if re.search('^wiki:', main_link):
                data = re.sub('\[\[((?:(?!\]\]).)+)\]\]', '<a id="inside" href="/' + tool.url_pas(main_link) + '">' + see_link + '</a>', data, 1)
            if re.search('^http(s)?:\/\/', main_link):
                data = re.sub('\[\[((?:(?!\]\]).)+)\]\]', '<a class="out_link" rel="nofollow" href="' + tool.url_pas(main_link) + '">' + see_link + '</a>', data, 1)
            else:
                if re.search('^:', main_link):
                    main_link = re.sub('^:', '', main_link)

                curs.execute("select title from data where title = ?", [main_link])
                if not curs.fetchall():
                    link_class = 'class="not_thing"'
                else:
                    link_class = ''

                data = re.sub('\[\[((?:(?!\]\]).)+)\]\]', '<a ' + link_class + ' href="/w/' + tool.url_pas(main_link) + '">' + see_link + '</a>', data, 1)
        else:
            break
    
    # 마지막 처리
    data = re.sub('(?P<in><hr id="under_bar" style="margin-top: -5px; margin-bottom: 10px;">)\r\n', '\g<in>', data)
    data = re.sub('<\/ul>\r\n\r\n', '</ul>\r\n', data)
    data = re.sub('\r\n', '<br>', data)

    return data