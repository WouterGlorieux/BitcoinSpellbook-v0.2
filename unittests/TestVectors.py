#!/usr/bin/env python
# -*- coding: utf-8 -*-

#example test vector
# [input, expected_output, description]

address_test_vectors = [
    ['1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y', True, "Normal valid address"],
    [u'1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y', True, "unicode valid address"],
    ['1SansacmMr38bdzGkzruDVajEsZuiZHx9', True, "Normal valid address"],
    ['1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8', True, "Normal valid address"],
    ['3AL6xh1qn4m83ni9vfTh6WarHBn1Ew1CZk', True, "Multisig valid address"],
    ['4Robbk6PuJst6ot6ay2DcVugv8nxfJh5y', False, "invalid address, starts with 4"],
    ['1Rlbbk6PuJst6ot6ay2DcVugv8nxfJh5y', False, "invalid address, contains l"],
    ['1RObbk6PuJst6ot6ay2DcVugv8nxfJh5y', False, "invalid address, contains O"],
    ['1RIbbk6PuJst6ot6ay2DcVugv8nxfJh5y', False, "invalid address, contains I"],
    ['123456789a123456789a12345', False, "address shorter than 26 characters"],
    ['123456789a123456789a123456789a123456', False, "address longer than 35 characters"],
    ['', False, 'empty string'],
    [None, False, 'None value'],
]

addresses_test_vectors = [
    ['1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y|1SansacmMr38bdzGkzruDVajEsZuiZHx9', True, "valid addresses"],
    [u'1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y|1SansacmMr38bdzGkzruDVajEsZuiZHx9', True, "valid addresses"],
    ['1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y,1SansacmMr38bdzGkzruDVajEsZuiZHx9', False, "separator , instead of |"],
    ['4Robbk6PuJst6ot6ay2DcVugv8nxfJh5y|1SansacmMr38bdzGkzruDVajEsZuiZHx9', False, "invalid first address"],
    ['1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y|4SansacmMr38bdzGkzruDVajEsZuiZHx9', False, "invalid second address"],
    ['', False, 'empty string'],
    [None, False, 'None value'],
]

profile_message_test_vectors = [
    ['@0:NAME=Robb Stark', True, 'valid message'],
    ['@0:NAME=Sansa Stark', True, 'valid message'],
    ['@0:HOUSE=Stark|@1:HOUSE=Stark', True, 'valid message'],
    ['0@1:RELATION=Brother|1@0:RELATION=Sister', True, 'valid message'],
    ['this message has exactly 80 characters and should be accepted by the blockchain!', False, 'invalid message'],
    ['test', False, 'invalid message'],
    ['@0:HOUSEStark|@1:HOUSE=Stark', False, 'invalid first part'],
    ['@0:HOUSE=Stark|@1:HOUSEStark', False, 'invalid second part'],
    ['0:NAME=Robb Stark', False, 'no @ character'],
    ['@0NAME=Robb Stark', False, 'no : character'],
    ['@0:NAMERobb Stark', False, 'no = character'],
    ['d@0:NAME=Robb Stark', False, 'FROM is not an integer or empty'],
    ['@d:NAME=Robb Stark', False, 'TO is not an integer'],
    ['@0:N_AME=Robb Stark', False, '_ in variable name'],
    ['@0:N AME=Robb Stark', False, 'whitespace in variable name'],
    ['@0:NAME=Robb? Stark', False, '? character in value'],
    ['@0:NAME=Robb\nStark', False, 'newline character in value'],
    ['@0:NAME=Robb\rStark', False, 'return character in value'],
    ['@0:NAME=Robb\tStark', False, 'tab character in value'],
    ['@0:NAME=Robb\fStark', False, 'form feed character in value'],
    ['', False, 'empty string'],
    [None, False, 'None value'],
]

txid_test_vectors = [
    ['bdd523f0171814cc1dcd28cb851ba9e68eb8f26eca03e4d3b0d0c6ca7d20d0b7', True, 'valid txid'],
    ['Bdd523f0171814cc1dcd28cb851ba9e68eb8f26eca03e4d3b0d0c6ca7d20d0b7', False, 'captital B'],
    ['gdd523f0171814cc1dcd28cb851ba9e68eb8f26eca03e4d3b0d0c6ca7d20d0b7', False, 'letter g'],
    ['bdd523f0171814cc1dcd28cb851ba9e68eb8f26eca03e4d3b0d0c6ca7d20d0b', False, '63 characters'],
    ['bdd523f0171814cc1dcd28cb851ba9e68eb8f26eca03e4d3b0d0c6ca7d20d0b77', False, '64 characters'],
    ['', False, 'empty string'],
    [None, False, 'None value'],
]

xpub_test_vectors = [
    ['xpub6CUvzHsNLcxthhGJesNDPSh2gicdHLPAAeyucP2KW1vBKEMxvDWCYRJZzM4g7mNiQ4Zb9nG4y25884SnYAr1P674yQipYLU8pP5z8AmahmD', True, 'valid xpub'],
    ['6CUvzHsNLcxthhGJesNDPSh2gicdHLPAAeyucP2KW1vBKEMxvDWCYRJZzM4g7mNiQ4Zb9nG4y25884SnYAr1P674yQipYLU8pP5z8AmahmD', False, 'no xpub at beginning'],
    ['', False, 'empty string'],
    [None, False, 'None value'],
]

description_test_vectors = [
    ['this is a valid description', True, 'valid description'],
    ['aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', False, 'too long'],
    ['', True, 'empty string'],
    [None, False, 'None value'],
]

op_return_test_vectors = [
    ['test', True, 'valid op_return'],
    ['aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', False, 'invalid op_return: 81 characters'],
    ['', False, 'empty string'],
    [None, False, 'None value'],
]

text_test_vectors = [
    ['qsddsqfazer', True, 'valid text'],
    [123456, False, 'invalid text'],
    ['', True, 'empty string'],
    [None, False, 'None value'],
]

url_test_vectors = [
    ['http://www.valyrian.tech', True, 'valid url'],
    ['www.valyrian.tech', True, 'valid url'],
    ['http://foo.com/blah_blah', True, 'valid url'],
    ['http://foo.com/blah_blah/', True, 'valid url'],
    ['http://foo.com/blah_blah_(wikipedia)', True, 'valid url'],
    ['http://foo.com/blah_blah_(wikipedia)_(again)', True, 'valid url'],
    ['http://www.example.com/wpstyle/?p=364', True, 'valid url'],
    ['https://www.example.com/foo/?bar=baz&inga=42&quux', True, 'valid url'],
    ['http://userid:password@example.com:8080', True, 'valid url'],
    ['http://userid:password@example.com:8080/ 	', True, 'valid url'],
    ['http://userid@example.com', True, 'valid url'],
    ['http://userid@example.com/', True, 'valid url'],
    ['http://userid@example.com:8080', True, 'valid url'],
    ['http://userid@example.com:8080/', True, 'valid url'],
    ['http://userid:password@example.com', True, 'valid url'],
    ['http://userid:password@example.com/', True, 'valid url'],
    ['http://142.42.1.1/', True, 'valid url'],
    ['http://142.42.1.1:8080/', True, 'valid url'],
    ['http://foo.com/blah_(wikipedia)#cite-1', True, 'valid url'],
    ['http://foo.com/(something)?after=parens', True, 'valid url'],
    ['http://code.google.com/events/#&product=browser', True, 'valid url'],
    ['http://foo.bar/?q=Test%20URL-encoded%20stuff', True, 'valid url'],
    ["http://-.~_!$&'()*+,;=:%40:80%2f::::::@example.com", True, 'valid url'],
    ['http://1337.net', True, 'valid url'],
    ['http://a.b-c.de', True, 'valid url'],
    ['http://223.255.255.254', True, 'valid url'],
    ['http://', False, 'invalid url'],
    #['http://.', False, 'invalid url'],
    #['http://..', False, 'invalid url'],
    #['http://foo.bar?q=Spaces should be encoded', False, 'spaces should be encoded'],
    ['http:// shouldfail.com', False, 'invalid url'],
    ['www.google.com', True, 'valid url'],
    [123456, False, 'invalid url'],
    ['', False, 'empty string'],
    [None, False, 'None value'],
]

creator_test_vectors = [
    ['Wouter Glorieux', True, 'valid creator'],
    [123456, False, 'invalid creator'],
    ['', False, 'empty string'],
    [None, False, 'None value'],
]

email_test_vectors = [
    ['info@valyrian.tech', True, 'valid email'],
    ['infovalyrian.tech', False, 'invalid email, no @'],
    ['info@valyriantech', False, 'invalid email, no . in domain'],
    ['', False, 'empty string'],
    [None, False, 'None value'],
]

amount_test_vectors = [
    [0, True, 'valid amount: 0'],
    [1, True, 'valid amount: 1'],
    [-1, False, 'negative amount'],
    [1.5, False, 'floating point number'],
    ['a', False, 'string'],
    ['', False, 'empty string'],
    [None, False, 'None value'],
]

block_height_test_vectors = [
    [0, True, 'valid block_height: 0'],
    [1, True, 'valid block_height: 1'],
    [350000, True, 'valid block_height: 350000'],
    [-1, False, 'negative number'],
    [1.5, False, 'floating point number'],
    ['', False, 'empty string'],
    [None, False, 'None value'],
]

percentage_test_vectors = [
    [0, True, 'valid percentage: 0'],
    [1, True, 'valid percentage: 1'],
    [50, True, 'valid percentage: 50'],
    [100, True, 'valid percentage: 100'],
    [-1, False, 'negative number'],
    [100.1, False, 'higher than 100'],
    [1.5, True, 'floating point number'],
    ['', False, 'empty string'],
    [None, False, 'None value'],
]

youtube_test_vectors = [
    ['http://youtu.be/C0DPdy98e4c', True, 'valid youtube id'],
    ['http://www.youtube.com/watch?v=lK-zaWCp-co&feature=g-all-u&context=G27a8a4aFAAAAAAAAAAA', True, 'valid youtube id'],
    ['http://youtu.be/AXaoi6dz59A', True, 'valid youtube id'],
    ['youtube.com/watch?gl=NL&hl=nl&feature=g-vrec&context=G2584313RVAAAAAAAABA&v=35LqQPKylEA', True, 'valid youtube id'],
    ['https://youtube.com/watch?gl=NL&hl=nl&feature=g-vrec&context=G2584313RVAAAAAAAABA&v=35LqQPKylEA', True, 'valid youtube id'],
    [0, False, 'invalid id'],
    ['', False, 'empty string'],
    ['www.youtube.com', False, 'no video id'],
    ['http://www.mytube.com/watch?v=35LqQPKylEA', False, 'mytube.com'],
    [None, False, 'None value'],
]

youtube_id_test_vectors = [
    ['C0DPdy98e4c', True, 'valid youtube id'],
    ['C0DPdy98e4', False, 'too short'],
    ['C0DPdy98e4c1', False, 'too long'],
    [0, False, 'invalid id'],
    ['', False, 'empty string'],
    ['www.youtube.com', False, 'no video id'],
    [None, False, 'None value'],
]


private_key_test_vectors = [
    ['KyH94vd8icQJ67aqqLRT5p33YFtYSgkGTdMWYA2suZaNJrjxNnFY', True, 'valid private key'],
    ['KwWu5FynetG6q8n7kzEmgdGtx3F5J9fQhvukQb9mCXCTpyzjoVtk', True, 'valid private key'],
    ['L4BgVKq9nibtSKsWyRMBrx78DnYVQNNzYNegtp4n2mtUZigA6a5P', True, 'valid private key'],
    ['L2ZC36oFWRvxqrD8PL6KCfM2zTjB4Z5bEdKmuqhbtLFg1c2a7xHg', True, 'valid private key'],
    ['5K2QLxgw38v1RD4CeEPW3eEbtXygSGstFsNUPr6aHAM6DRND1mW', True, 'valid private key'],
    [0, False, 'invalid private key: 0'],
    ['', False, 'empty string'],
    [None, False, 'None value'],
]

distribution_test_vectors = [
    [[[u'1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y', 100000, 0.1, 375786],
     [u'1SansacmMr38bdzGkzruDVajEsZuiZHx9', 400000, 0.4, 375790],
     [u'1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y', 500000, 0.5, 375786]], True, 'valid distribution'],
    [[[u'1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y', 'a', 0.1, 375786],
     [u'1SansacmMr38bdzGkzruDVajEsZuiZHx9', 400000, 0.4, 375790],
     [u'1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y', 500000, 0.5, 375786]], False, 'value not a integer'],
    [[[1, 100000, 0.1, 375786],
     [u'1SansacmMr38bdzGkzruDVajEsZuiZHx9', 400000, 0.4, 375790],
     [u'1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y', 500000, 0.5, 375786]], False, 'address not valid'],
    [[], False, 'empty list'],
    ['', False, 'empty string'],
    [None, False, 'None value'],
]

outputs_test_vectors = [
    [[('1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y', 50000), ('1SansacmMr38bdzGkzruDVajEsZuiZHx9', 50000)], True, 'valid outputs'],
    [[('1SansacmMr38bdzGkzruDVajEsZuiZHx9', 50000)], True, 'valid outputs'],
    [[('1SansacmMr38bdzGkzruDVajEsZuiZHx9', 'q')], False, 'invalid outputs: second parameter not an integer'],
    ['', False, 'empty string'],
    [None, False, 'None value'],
]