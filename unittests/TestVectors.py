#example test vector
# [input, expected_output, description]

address_test_vectors = [
    ['1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y',True, "Normal valid address"],
    ['1SansacmMr38bdzGkzruDVajEsZuiZHx9', True, "Normal valid address"],
    ['1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8', True, "Normal valid address"],
    ['3AL6xh1qn4m83ni9vfTh6WarHBn1Ew1CZk', True, "Multisig valid address"],
    ['4Robbk6PuJst6ot6ay2DcVugv8nxfJh5y', False, "invalid address, starts with 4"],
    ['1Rlbbk6PuJst6ot6ay2DcVugv8nxfJh5y', False, "invalid address, contains l"],
    ['1RObbk6PuJst6ot6ay2DcVugv8nxfJh5y',False,"invalid address, contains O"],
    ['1RIbbk6PuJst6ot6ay2DcVugv8nxfJh5y', False,"invalid address, contains I"],
    ['123456789a123456789a12345', False,"address shorter than 26 characters"],
    ['123456789a123456789a123456789a123456', False, "address longer than 35 characters"],
]


addresses_test_vectors = [
    ['1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y|1SansacmMr38bdzGkzruDVajEsZuiZHx9', True, "valid addresses"],
    ['1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y,1SansacmMr38bdzGkzruDVajEsZuiZHx9', False, "separator , instead of |"],
    ['4Robbk6PuJst6ot6ay2DcVugv8nxfJh5y|1SansacmMr38bdzGkzruDVajEsZuiZHx9', False, "invalid first address"],
    ['1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y|4SansacmMr38bdzGkzruDVajEsZuiZHx9', False, "invalid second address"],
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
]