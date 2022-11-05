from time import time
import matplotlib.pyplot as plt
import os.path
from simulation.Logs import Logs
from network.IntelligentNode import IntelligentNode
from operator import add
import numpy as np
import random


class Simulation:
    def __init__(self, G, c_n=10):
        self.G = G
        self.graph = G.graph
        self.n = G.n
        self.c_n = c_n
        self.alpha = -1
        self.log_simulation = Logs("simulation.txt")
        self.log_packet = Logs("packets.txt")
        self.arrived_packets = []
        self.figure1 = [[], []]  # l, átlagos sorhossz
        self.figure2 = [[], []]  # l, csomagok átlag úthossza
        self.figure3 = [[], []]  # l, távolság
        self.figure4 = [[], [], []]  # fix N_L [fokszámok][l - x] [n_l - y] csomópontok átlagos sorhossza
        self.figure5 = [[], [], []]  # fix P_L [fokszámok][l - x] [p_l - y] csomagok átlagos élettartama
        self.fig_R_L_t = [[], []]  # átlagos úthoszza a célba ért csomagoknak [[l], [[sum_úthoszak/|D|],[sum_úthoszak/|D|], ..]]
        self.fig_n_o_t = [[], []]  # túlterhelt csomópontok száma [[l], [[túlterhelt csomópontok száma],[],[]...]]
        self.fig_n_pio_t = [[], []]  # túlterhelt csomópontokban a csomagok száma [[l],[[npio],[],...]]
        self.fig_pa_t = [[], []]  # beérkezett csomagok aránya
        self.fig_data = [[], [[], [], [], []]]  # counter, K=0, K=1, K=2, K=5
        self.times_list = [[], []]  # num int node
        self.sim_time = 500
        self.sim_counter = 10  # hányszor fusson a szimuláció

    def close_files(self):
        self.log_simulation.close()
        self.log_packet.close()

    # counter = l időpillanatokban generálódó csomagok
    def start(self):
        self.log_simulation.log("Start\n")
        print("Start simulation - diff K")
        self.G.remove_all_int_node()
        self.G.clear_queue()
        self.log_simulation.log("Csomag generálás kezdés \n")
        counter = [10, 15, 20, 25, 30, 35]
        percent_int_node = [0, 0.01, 0.02, 0.05]
        num_int_node = [item * self.n for item in percent_int_node]
        self.figure1[0] = counter
        self.figure2[0] = counter
        self.fig_R_L_t[0] = counter
        self.fig_n_o_t[0] = counter
        self.fig_n_pio_t[0] = counter
        self.fig_pa_t[0] = counter
        self.fig_data[0] = counter
        self.times_list[0] = percent_int_node
        self.figure1[1] = [[0 for _ in range(len(counter))] for _ in range(len(num_int_node))]
        self.figure2[1] = [[0 for _ in range(len(counter))] for _ in range(len(num_int_node))]
        self.fig_R_L_t[1] = [[0 for _ in range(len(counter))] for _ in range(len(num_int_node))]
        self.fig_n_o_t[1] = [[0 for _ in range(len(counter))] for _ in range(len(num_int_node))]
        self.fig_n_pio_t[1] = [[0 for _ in range(len(counter))] for _ in range(len(num_int_node))]
        self.fig_pa_t[1] = [[0 for _ in range(len(counter))] for _ in range(len(num_int_node))]
        self.fig_data[1] = [[[0 for _ in range(self.sim_time)]
                             for _ in range(len(counter))]
                            for _ in range(len(num_int_node))]
        self.times_list[1] = [0 for _ in num_int_node]
        for j in np.arange(self.sim_counter):
            print(str(j + 1) + '. futás')
            self.G.remove_all_int_node()
            for i in np.arange(len(num_int_node)):
                print("intnode = " + str(num_int_node[i]))
                self.clear_int_nodes()
                data = []
                pr_data = []
                data_R_L_t = []
                data_n_o_t = []
                data_n_pio_t = []
                data_pa_t = []
                data_adat0 = []
                while self.G.num_of_intelligent_node != num_int_node[i]:
                    self.G.add_new_intelligent_node()
                self.log_simulation.log("intelligens nodok szama: " + str(self.G.num_of_intelligent_node) + '\n')
                start_time = time()
                for l in counter:
                    self.clear_int_nodes()
                    print("l = " + str(l))
                    self.log_simulation.log("l = " + str(l) + '\n')
                    time_ = 1
                    data_adat1 = []
                    while time_ <= self.sim_time:
                        self.start_generate_packets(l, time_)
                        self.start_packet_forwarding(self.alpha, time_)
                        data_adat1.append(self.calculate_data(num_int_node[i]))
                        time_ += 1
                    data.append(self.node_queue_length_avg())
                    pr_data.append(self.arrived_packets_life_time())
                    data_n_o_t.append(self.n_o_and_n_pio()[0])
                    data_n_pio_t.append(self.n_o_and_n_pio()[1])
                    data_R_L_t.append(self.r_l_t())
                    data_pa_t.append(len(self.arrived_packets))
                    data_adat0.append(data_adat1)
                    self.G.clear_queue()
                    self.arrived_packets.clear()
                run_time = time() - start_time
                self.times_list[1][i] += run_time
                self.figure1[1][i] = list(map(add, self.figure1[1][i], data))
                self.figure2[1][i] = list(map(add, self.figure2[1][i], pr_data))
                self.fig_n_o_t[1][i] = list(map(add, self.fig_n_o_t[1][i], data_n_o_t))
                self.fig_n_pio_t[1][i] = list(map(add, self.fig_n_pio_t[1][i], data_n_pio_t))
                self.fig_R_L_t[1][i] = list(map(add, self.fig_R_L_t[1][i], data_R_L_t))
                self.fig_pa_t[1][i] = list(map(add, self.fig_pa_t[1][i], data_pa_t))
                self.fig_data[1][i] = np.add(self.fig_data[1][i], data_adat0)
                self.log_simulation.log("Futási idő: " + str(run_time) + " seconds\n")
        self.figure()
        print("End Simulation")

    def start_fix(self):
        print("Start simulation - 5% int node - diff edge num")
        self.G.remove_all_int_node()
        self.G.clear_queue()
        int_nodes_max = self.find_degree_nodes()[0]
        int_nodes_mid = self.find_degree_nodes()[1]  # ebbe kell egy alacsony, magas, és közepes fokszámú
        int_nodes_min = self.find_degree_nodes()[2]
        int_nodes = [[], int_nodes_max, int_nodes_mid, int_nodes_min]
        counter = [10, 15, 20, 25, 30, 35]  # node amiből intelligenset fogunk csinálni
        self.figure4[1] = counter
        self.figure5[1] = counter
        labels = ['nincs', 'magas', 'kozepes', 'alacsony']
        for i in range(4):
            print(labels[i])
            self.G.remove_all_int_node()
            if len(int_nodes[i]) != 0:
                for int_node in int_nodes[i]:
                    self.G.add_new_intelligent_node_in_id(int_node.id)
            data_n_l = []
            data_p_l = []
            for l in counter:
                self.clear_int_nodes()
                print("l = " + str(l))
                self.log_simulation.log("l = " + str(l) + '\n')
                time_ = 1
                while time_ <= self.sim_time:
                    self.start_generate_packets(l, time_)
                    self.start_packet_forwarding(self.alpha, time_)
                    time_ += 1
                data_n_l.append(self.node_queue_length_avg())
                data_p_l.append(self.arrived_packets_life_time())
                self.G.clear_queue()
                self.arrived_packets.clear()
            self.figure4[2].append(data_n_l)
            self.figure5[2].append(data_p_l)
        self.figure_fix_n_l()
        self.figure_fix_p_l()
        print('End simulation')

    def start_simple(self):
        self.log_simulation.log("Start\n")
        print("Start simulation - one int node")
        self.G.remove_all_int_node()
        self.G.clear_queue()
        self.log_simulation.log("Csomag generálás kezdés \n")
        counter = [10, 15, 20, 25, 30, 35]
        self.G.add_new_intelligent_node()
        for l in counter:
            self.clear_int_nodes()
            print("l = " + str(l))
            self.log_simulation.log("l = " + str(l) + '\n')
            time_ = 1
            data_diff = []
            while time_ <= self.sim_time:
                self.start_generate_packets(l, time_)
                self.start_packet_forwarding(self.alpha, time_)
                data_diff.append(self.diff())
                time_ += 1
            self.figure3[1].append(data_diff)
            self.G.clear_queue()
            self.arrived_packets.clear()
        self.figure_diff()
        print('End Simulation - one int node')

    def find_degree_nodes(self):
        list_d_min = []
        list_d_max = []
        list_d_mid = []
        self.graph.sort(key=lambda x: x.degree())
        for i in range(10):
            list_d_max.append(self.graph[-i])  # max
            list_d_min.append(self.graph[i])  # min
        tmp_list = self.graph[20:-20]
        id_list = random.sample(range(len(tmp_list)), 10)
        for id in id_list:
            list_d_mid.append(self.graph[id])
        self.graph.sort(key=lambda x: x.id)
        return list_d_max, list_d_mid, list_d_min

    def start_generate_packets(self, l, birth_time):
        generated = []
        while len(generated) < l:
            tmp = np.random.randint(self.n)
            while tmp in generated:
                tmp = np.random.randint(self.n)
            generated.append(tmp)
        for i in generated:
            self.graph[i].generate_new_packet(birth_time)

    def start_packet_forwarding(self, alpha, die_time):
        for node in self.graph:
            i = 0
            is_next: bool = False
            while i < self.c_n and not is_next:
                next_node_id = node.get_next_node_id(alpha)
                if next_node_id == -1:
                    is_next = True
                elif next_node_id == -2:
                    node.clear_queue()
                    is_next = True
                elif next_node_id == -4:
                    is_next = True
                elif next_node_id == -3:
                    print("nincs ervenyes ut!")
                    is_next = True
                elif next_node_id is None:
                    is_next = True
                else:
                    packet = node.get_first_packet()
                    if next_node_id == packet.target:
                        self.arrived_packets.append(packet)
                        packet.arrived(die_time)
                    self.graph[next_node_id].accept_packet(packet)
                i += 1
        self.G.copy()

    def n_o_and_n_pio(self):
        counter_n_o = sum(map(lambda node: node.packet_list.size() > self.c_n, self.graph))
        counter_n_pio = sum(node.packet_list.size() for node in self.graph
                            if node.packet_list.size() > self.c_n)
        return counter_n_o, counter_n_pio

    def r_l_t(self):
        tmp = sum(len(a.route) for a in self.arrived_packets)
        return tmp / len(self.arrived_packets)

    def node_queue_length_avg(self):
        queue_length = sum(node.packet_list.size() for node in self.graph)
        return queue_length / self.n

    def arrived_packets_life_time(self):
        life_time_sum = sum(packet.life_time for packet in self.arrived_packets)
        return life_time_sum / len(self.arrived_packets)

    def calculate_data(self, num_int_node):
        if num_int_node != 0:
            return sum(node.get_data() for node in self.G.iterate_graph())
        else: #megszámoljuk hány csomag van a hálózatban perpill
            return sum(node.get_packets_num() for node in self.G.iterate_graph())

    def clear_int_nodes(self):
        for node in self.graph:
            if isinstance(node, IntelligentNode):
                node.clear()

    def diff(self):
        tmp = []
        for node in self.graph:
            if isinstance(node, IntelligentNode):
                tmp.append(self.G.all_link() - node.diff())
        return tmp

    def figure_fix_n_l(self):
        x = self.figure4[1]
        y0 = [a / self.n for a in self.figure4[2][0]]
        y1 = [a / self.n for a in self.figure4[2][1]]
        y2 = [a / self.n for a in self.figure4[2][2]]
        y3 = [a / self.n for a in self.figure4[2][3]]
        plt.grid(True)
        plt.plot(x, y0, 'yo', label='K=0')
        plt.plot(x, y0, '--y')
        plt.plot(x, y1, 'ro', label='magas')
        plt.plot(x, y1, 'r')
        plt.plot(x, y2, 'bo', label='közepes')
        plt.plot(x, y2, 'b')
        plt.plot(x, y3, 'go', label='alacsony')
        plt.plot(x, y3, 'g')
        plt.legend()
        plt.xlabel("L")
        plt.ylabel('$N_L$(' + str(self.sim_time) + ')')
        complete_name = os.path.join('./logs', 'N_L_kul_fokszamu_int_node_t'
                                     + str(self.sim_time) + '_N' + str(self.n)
                                     + '_' + self.G.network_type + '_' + self.G.packet_type
                                     + '.png')
        plt.savefig(complete_name)
        plt.close()

    def figure_fix_p_l(self):
        x = self.figure5[1]
        y0 = self.figure5[2][0]
        y1 = self.figure5[2][1]
        y2 = self.figure5[2][2]
        y3 = self.figure5[2][3]
        plt.grid(True)
        plt.plot(x, y0, 'yo', label='K=0')
        plt.plot(x, y0, '--y')
        plt.plot(x, y1, 'ro', label='magas')
        plt.plot(x, y1, 'r')
        plt.plot(x, y2, 'bo', label='közepes')
        plt.plot(x, y2, 'b')
        plt.plot(x, y3, 'go', label='alacsony')
        plt.plot(x, y3, 'g')
        plt.legend()
        plt.xlabel("L")
        plt.ylabel('$P_L$(' + str(self.sim_time) + ')')
        complete_name = os.path.join('./logs', "P_L_kul_fokszamu_int_node_t"
                                     + str(self.sim_time) + "_N" + str(self.n)
                                     + "_" + self.G.network_type + "_" + self.G.packet_type
                                     + ".png")
        plt.savefig(complete_name)
        plt.close()

    def figure_n_l_t(self):
        x = self.figure1[0]
        y0 = [a / self.sim_counter for a in self.figure1[1][0]]
        y1 = [a / self.sim_counter for a in self.figure1[1][1]]
        y2 = [a / self.sim_counter for a in self.figure1[1][2]]
        y3 = [a / self.sim_counter for a in self.figure1[1][3]]
        plt.grid(True)
        plt.plot(x, y0, 'yo', label='K=0%')
        plt.plot(x, y0, '--y')
        plt.plot(x, y1, 'go', label='K=1%')
        plt.plot(x, y1, '--g')
        plt.plot(x, y2, 'bo', label='K=2%')
        plt.plot(x, y2, '--b')
        plt.plot(x, y3, 'ro', label='K=5%')
        plt.plot(x, y3, '--r')
        plt.legend()
        plt.xlabel("L")
        plt.ylabel('$N_L$(' + str(self.sim_time) + ')')
        complete_name = os.path.join('./logs', "Atlagos_sor_hossz_t"
                                     + str(self.sim_time) + "_N" + str(self.n)
                                     + "_" + self.G.network_type + "_" + self.G.packet_type
                                     + ".png")
        plt.savefig(complete_name)
        plt.close()

    def figure_p_l_t(self):
        plt.grid(True)
        x = self.figure2[0]
        y0 = [a / self.sim_counter for a in self.figure2[1][0]]
        y1 = [a / self.sim_counter for a in self.figure2[1][1]]
        y2 = [a / self.sim_counter for a in self.figure2[1][2]]
        y3 = [a / self.sim_counter for a in self.figure2[1][3]]
        plt.plot(x, y0, 'yo', label='K=0%')
        plt.plot(x, y0, '--y')
        plt.plot(x, y1, 'go', label='K=1%')
        plt.plot(x, y1, '--g')
        plt.plot(x, y2, 'bo', label='K=2%')
        plt.plot(x, y2, '--b')
        plt.plot(x, y3, 'ro', label='K=5%')
        plt.plot(x, y3, '--r')
        plt.legend()
        plt.xlabel("L")
        plt.ylabel("$P_L$(" + str(self.sim_time) + ")")
        complete_name = os.path.join('./logs', "Atlagos_elet_tartam_t"
                                     + str(self.sim_time) + "_N" + str(self.n)
                                     + "_" + self.G.network_type + "_" + self.G.packet_type
                                     + ".png")
        plt.savefig(complete_name)
        plt.close()

    def figure_diff(self):
        plt.grid(True)
        x = range(500)
        y0 = self.figure3[1][0]
        y2 = self.figure3[1][2]
        y5 = self.figure3[1][5]
        plt.plot(x, y0, 'g', label='L=10')
        plt.plot(x, y2, 'b', label='L=20')
        plt.plot(x, y5, 'r', label='L=35')
        plt.legend()
        plt.xlabel('t')
        plt.ylabel(r'd($\mathbf{A}_r, \mathbf{A}_{n_i}$)(t)')
        complete_name = os.path.join('./logs', "Diff_t"
                                     + str(self.sim_time) + "_N" + str(self.n)
                                     + "_" + self.G.network_type + "_" + self.G.packet_type
                                     + ".png")
        plt.savefig(complete_name)
        plt.close()

    def figure_time(self):
        plt.grid(True)
        x = [a * 100 for a in self.times_list[0]]
        y = [a / self.sim_counter for a in self.times_list[1]]
        plt.plot(x, y, 'ro', x, y, '--r')
        plt.ylabel("t(s)")
        plt.xlabel("K")
        complete_name = os.path.join('./logs', "Futasi_ido"
                                     + str(self.sim_time) + "_N" + str(self.n)
                                     + "_" + self.G.network_type + "_" + self.G.packet_type
                                     + ".png")
        plt.savefig(complete_name)
        plt.close()

    def figure_R_L_t(self):
        plt.grid(True)
        x = self.fig_R_L_t[0]
        y0 = [a / self.sim_counter for a in self.fig_R_L_t[1][0]]
        y1 = [a / self.sim_counter for a in self.fig_R_L_t[1][1]]
        y2 = [a / self.sim_counter for a in self.fig_R_L_t[1][2]]
        y3 = [a / self.sim_counter for a in self.fig_R_L_t[1][3]]
        plt.plot(x, y0, 'yo', label='K=0%')
        plt.plot(x, y0, '--y')
        plt.plot(x, y1, 'go', label='K=1%')
        plt.plot(x, y1, '--g')
        plt.plot(x, y2, 'bo', label='K=2%')
        plt.plot(x, y2, '--b')
        plt.plot(x, y3, 'ro', label='K=5%')
        plt.plot(x, y3, '--r')
        plt.legend()
        plt.xlabel("L")
        plt.ylabel("$R_L$(" + str(self.sim_time) + ")")
        complete_name = os.path.join('./logs', "Atlagos_ut_hossz_t"
                                     + str(self.sim_time) + "_N" + str(self.n)
                                     + "_" + self.G.network_type + "_" + self.G.packet_type
                                     + ".png")
        plt.savefig(complete_name)
        plt.close()

    def figure_n_o_t(self):
        plt.grid(True)
        x = self.fig_n_o_t[0]
        y0 = [a / self.sim_counter for a in self.fig_n_o_t[1][0]]
        y1 = [a / self.sim_counter for a in self.fig_n_o_t[1][1]]
        y2 = [a / self.sim_counter for a in self.fig_n_o_t[1][2]]
        y3 = [a / self.sim_counter for a in self.fig_n_o_t[1][3]]
        plt.plot(x, y0, 'yo', label='K=0%')
        plt.plot(x, y0, '--y')
        plt.plot(x, y1, 'go', label='K=1%')
        plt.plot(x, y1, '--g')
        plt.plot(x, y2, 'bo', label='K=2%')
        plt.plot(x, y2, '--b')
        plt.plot(x, y3, 'ro', label='K=5%')
        plt.plot(x, y3, '--r')
        plt.legend()
        plt.xlabel("L")
        plt.ylabel("$n_o$(" + str(self.sim_time) + ")")
        complete_name = os.path.join('./logs', "n_o_t"
                                     + str(self.sim_time) + "_N" + str(self.n)
                                     + "_" + self.G.network_type + "_" + self.G.packet_type
                                     + ".png")
        plt.savefig(complete_name)
        plt.close()

    def figure_n_pio_t(self):
        plt.grid(True)
        x = self.fig_n_pio_t[0]
        y0 = [a / self.sim_counter for a in self.fig_n_pio_t[1][0]]
        y1 = [a / self.sim_counter for a in self.fig_n_pio_t[1][1]]
        y2 = [a / self.sim_counter for a in self.fig_n_pio_t[1][2]]
        y3 = [a / self.sim_counter for a in self.fig_n_pio_t[1][3]]
        plt.plot(x, y0, 'yo', label='K=0%')
        plt.plot(x, y0, '--y')
        plt.plot(x, y1, 'go', label='K=1%')
        plt.plot(x, y1, '--g')
        plt.plot(x, y2, 'bo', label='K=2%')
        plt.plot(x, y2, '--b')
        plt.plot(x, y3, 'ro', label='K=5%')
        plt.plot(x, y3, '--r')
        plt.legend()
        plt.xlabel("L")
        plt.ylabel("$n_pio$(" + str(self.sim_time) + ")")
        complete_name = os.path.join('./logs', "n_pio_t"
                                     + str(self.sim_time) + "_N" + str(self.n)
                                     + "_" + self.G.network_type + "_" + self.G.packet_type
                                     + ".png")
        plt.savefig(complete_name)
        plt.close()

    def figure_pa_t(self):
        plt.grid(True)
        x = self.fig_pa_t[0]
        y = [self.sim_time * i for i in x]
        print(self.fig_pa_t)
        y0 = [(a / self.sim_counter) / i for a, i in zip(self.fig_pa_t[1][0], y)]
        y1 = [(a / self.sim_counter) / i for a, i in zip(self.fig_pa_t[1][1], y)]
        y2 = [(a / self.sim_counter) / i for a, i in zip(self.fig_pa_t[1][2], y)]
        y3 = [(a / self.sim_counter) / i for a, i in zip(self.fig_pa_t[1][3], y)]
        plt.plot(x, y0, 'yo', label='K=0%')
        plt.plot(x, y0, '--y')
        plt.plot(x, y1, 'go', label='K=1%')
        plt.plot(x, y1, '--g')
        plt.plot(x, y2, 'bo', label='K=2%')
        plt.plot(x, y2, '--b')
        plt.plot(x, y3, 'ro', label='K=5%')
        plt.plot(x, y3, '--r')
        plt.legend()
        plt.xlabel("L")
        plt.ylabel("$p_a($" + str(self.sim_time) + ")")
        complete_name = os.path.join('./logs', "pa_t"
                                     + str(self.sim_time) + "_N" + str(self.n)
                                     + "_" + self.G.network_type + "_" + self.G.packet_type
                                     + ".png")
        plt.savefig(complete_name)
        plt.close()

    def figure_D_t(self):
        plt.grid(True)
        x = self.fig_pa_t[0]
        y0 = [a / self.sim_counter for a in self.fig_pa_t[1][0]]
        y1 = [a / self.sim_counter for a in self.fig_pa_t[1][1]]
        y2 = [a / self.sim_counter for a in self.fig_pa_t[1][2]]
        y3 = [a / self.sim_counter for a in self.fig_pa_t[1][3]]
        y4 = [self.sim_time * i for i in x]
        plt.plot(x, y0, 'yo', label='K=0%')
        plt.plot(x, y0, '--y')
        plt.plot(x, y1, 'go', label='K=1%')
        plt.plot(x, y1, '--g')
        plt.plot(x, y2, 'bo', label='K=2%')
        plt.plot(x, y2, '--b')
        plt.plot(x, y3, 'ro', label='K=5%')
        plt.plot(x, y3, '--r')
        plt.plot(x, y4, 'mo', label='|$D_L(500)$|')
        plt.plot(x, y4, '--m')
        plt.legend()
        plt.xlabel("L")
        plt.ylabel("$|D($" + str(self.sim_time) + ")|")
        complete_name = os.path.join('./logs', "D_t"
                                     + str(self.sim_time) + "_N" + str(self.n)
                                     + "_" + self.G.network_type + "_" + self.G.packet_type
                                     + ".png")
        plt.savefig(complete_name)
        plt.close()

    def figure_data(self):
        plt.grid(True)
        x = range(self.sim_time)
        y0 = self.fig_data[1][0][0]                # l=10
        y2 = self.fig_data[1][0][2]                # l=20
        y5 = self.fig_data[1][0][5]                # l=35
        plt.plot(x, y0, 'y', label='L=10')
        plt.plot(x, y2, 'b', label='L=20')
        plt.plot(x, y5, 'r', label='L=35')
        plt.legend()
        plt.yscale("log")
        plt.xlabel("t(s)")
        plt.ylabel("<N(" + str(self.sim_time) + ")>(bit)")
        complete_name = os.path.join('./logs', "data_K0_"
                                     + str(self.sim_time) + "_N" + str(self.n)
                                     + "_" + self.G.network_type + "_" + self.G.packet_type
                                     + ".png")
        plt.savefig(complete_name)
        plt.close()

        plt.grid(True)
        x = range(self.sim_time)
        y0 = self.fig_data[1][1][0]  # l=10
        y2 = self.fig_data[1][1][2]  # l=20
        y5 = self.fig_data[1][1][5]  # l=35
        plt.plot(x, y0, 'y', label='L=10')
        plt.plot(x, y2, 'b', label='L=20')
        plt.plot(x, y5, 'r', label='L=35')
        plt.legend()
        plt.yscale("log")
        plt.xlabel("t(s)")
        plt.ylabel("<N(" + str(self.sim_time) + ")>(bit)")
        complete_name = os.path.join('./logs', "data_K1_"
                                     + str(self.sim_time) + "_N" + str(self.n)
                                     + "_" + self.G.network_type + "_" + self.G.packet_type
                                     + ".png")
        plt.savefig(complete_name)
        plt.close()

        plt.grid(True)
        x = range(self.sim_time)
        y0 = self.fig_data[1][2][0]  # l=10
        y2 = self.fig_data[1][2][2]  # l=20
        y5 = self.fig_data[1][2][5]  # l=35
        plt.plot(x, y0, 'y', label='L=10')
        plt.plot(x, y2, 'b', label='L=20')
        plt.plot(x, y5, 'r', label='L=35')
        plt.legend()
        plt.yscale("log")
        plt.xlabel("t(s)")
        plt.ylabel("<N(" + str(self.sim_time) + ")>(bit)")
        complete_name = os.path.join('./logs', "data_K2_"
                                     + str(self.sim_time) + "_N" + str(self.n)
                                     + "_" + self.G.network_type + "_" + self.G.packet_type
                                     + ".png")
        plt.savefig(complete_name)
        plt.close()

        plt.grid(True)
        x = range(self.sim_time)
        y0 = self.fig_data[1][3][0]  # l=10
        y2 = self.fig_data[1][3][2]  # l=20
        y5 = self.fig_data[1][3][5]  # l=35
        plt.plot(x, y0, 'y', label='L=10')
        plt.plot(x, y2, 'b', label='L=20')
        plt.plot(x, y5, 'r', label='L=35')
        plt.legend()
        plt.yscale("log")
        plt.xlabel("t")
        plt.ylabel("<N(" + str(self.sim_time) + ")>(bit)")
        complete_name = os.path.join('./logs', "data_K5_"
                                     + str(self.sim_time) + "_N" + str(self.n)
                                     + "_" + self.G.network_type + "_" + self.G.packet_type
                                     + ".png")
        plt.savefig(complete_name)
        plt.close()

    def figure(self):
        self.figure_p_l_t()
        self.figure_n_l_t()
        self.figure_n_pio_t()
        self.figure_n_o_t()
        self.figure_R_L_t()
        self.figure_pa_t()
        self.figure_D_t()
        self.figure_time()
        self.figure_data()
