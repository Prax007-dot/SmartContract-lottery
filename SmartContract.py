import smartpy as sp

class Lottery(sp.Contract):
    def __init__(self):
        self.init(
            players= sp.map(l={},tkey=sp.TNat,tvalue=sp.TAddress),
            ticket_cost=sp.tez(1),
            tickets_available=sp.nat(5),
            max_tickets=sp.nat(5),
            operator= sp.test_account("admin").address,
        )       

    @sp.entry_point
    def buy_ticket(self):
        
        #assertion
        sp.verify(self.data.tickets_available>0,"No Tickets Available")
        sp.verify(sp.amount>=self.data.ticket_cost,"Inalid Amount")

        #storage changes
        self.data.players[sp.len(self.data.players)]=sp.sender
        self.data.tickets_available = sp.as_nat(self.data.tickets_available-1)

        #return extra tez
        extra_balance = sp.amount-self.data.ticket_cost
        sp.if extra_balance > sp.mutez(0):
            sp.send(sp.sender, extra_balance)
    
    @sp.entry_point
    def end_game(self, random_number):
        sp.set_type(random_number, sp.TNat)

        #assertion
        sp.verify(self.data.tickets_available==0,"Tickets are not finished so game will not end")
        sp.verify(sp.sender == self.data.operator,"Not Authorised")

        #generate winning index
        winner_index=random_number % self.data.max_tickets
        winner_address = self.data.players[winner_index]
        sp.send(winner_address, sp.balance)

        self.data.players={}
        self.data.tickets_available=self.data.max_tickets


    @sp.add_test(name="main")
    def test():
        scenario = sp.test_scenario()

        #test account
        admin=sp.test_account("admin")
        alice=sp.test_account("alice")
        bob=sp.test_account("bob")
        jacob=sp.test_account("jacob")
        lily=sp.test_account("lily")
        bruce=sp.test_account("bruce")

        #Contratct instance
        lottery = Lottery()
        scenario += lottery

        #buy_ticket
        scenario += lottery.buy_ticket().run(
            amount= sp.tez(1), sender=alice
        )

        scenario += lottery.buy_ticket().run(
            amount= sp.tez(1), sender=bob
        )

        scenario += lottery.buy_ticket().run(
            amount= sp.tez(1), sender=jacob
        )

        scenario += lottery.buy_ticket().run(
            amount= sp.tez(1), sender=lily
        )

        scenario += lottery.buy_ticket().run(
            amount= sp.tez(4), sender=bruce
        )

        #endgame
        scenario += lottery.end_game(25).run(now=sp.timestamp(3), sender = admin)
