def get_itc_increment(votes: dict, atc):
    itc = 0
    for p_id, v in votes.items():
        itc += abs(v - atc)
    return itc

#
# def get_next_loss(votes, loss, atc):
#     """
#     Calculate loss of all the persons if take this input atc
#     Note: the votes may include a part of people
#     :param votes: dict, votes
#     :param loss: dict, current loss
#     :param atc: int, the aggregated thermal comfort to be taken
#     :return: dict, extra loss of all persons
#     """
#     loss_new = loss
#     avg_loss = 0
#
#     # calculate the average loss
#     for v in votes.values():
#         avg_loss += abs(atc - v)
#     avg_loss /= len(votes)
#
#     # each add extra loss
#     for key, value in votes.items():
#         # loss
#         a = abs(atc - value)
#         # extra loss
#         b = a - avg_loss
#         loss_new[key] = loss[key] + b
#
#     return loss_new


class Result:

    his_ec = {}
    pointer_ec = 0
    his_itc = {}
    pointer_itc = 0
    his_tce = {}
    pointer_tce = 0

    def __init__(self):
        self.ec_clg = 0
        self.ec_htg = 0
        self.itc = 0
        self.tce = 0
        # TODO: open files and write when reset

    def add_consumption(self, consumption_clg, consumption_htg, demand):
        if demand == "clg":
            self.ec_clg += consumption_clg
        else:
            self.ec_htg += consumption_htg

    def update_itc(self, votes: dict, atc: dict):
        for space_id, votes_space in votes.items():
            if atc[space_id] == 4 or len(votes_space) == 0:
                continue
            self.itc += get_itc_increment(votes_space, atc[space_id])

    def reset(self):
        self.ec_clg = 0
        self.itc = 0
        # TODO: write result to files

