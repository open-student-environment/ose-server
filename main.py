import json
from flask_cors import CORS
from flask import Flask
from flask_restful import Resource, Api, reqparse
from ose.statement import load_statements
from ose.agent import load_agents
from ose.environment import Environment, get_active_agents, filter_by_users
import numpy as np
from collections import defaultdict
import datetime

names = ['Abdul Lepez', 'Abel Zebuth', 'Abraham Kivive', 'Achille Ahonte', 'Achille Londumur', 'Achille Parmentier', 'Adelina Ottension', 'Adolf Herkanmem', 'Adolphine Champagne', 'Agatha Stroff', 'Agathe Patsurlamokett', 'Agathe Youbeybe', 'Agathe Zeblouse', 'Agostinho Ranscras', 'Ahmed Ametlatable', 'Ahmed Epan', 'Akim Enculbien', 'Alain Continent', 'Alain Di', 'Alain Pertinent', 'Alain Petigo', 'Alain Posteur', 'Alain Puissant', 'Alain Verty', 'Alan Biquet', 'Alban Dapard', 'Albert Gamotte', 'Albert Mudat', 'Al Bibach', 'Albin Turk', 'Aldebert Nicle', 'Alcide Gastric', 'Aldo Curbet', 'Aldo Vergne', 'Alec Houillapla', 'Alexandre Hopoze', 'Alex Cargo', 'Alex Kuzbidon', 'Alex Voto', 'Alex Ylophage', 'Alfonso Toilette', 'Alfred Aibaitiz', 'Alfred Bush', 'Alfred Transport', 'Ali Abaldakin', 'Alibert Assion', 'Ali Bideau', 'Alice Moitranquille', 'Ali Gator', 'Ali Go', 'Ali Pitivinblanc', 'Alonzo Balmasquez', 'Alphonse Danltas', 'Alyson Leyklosh', 'Amadou Douh', 'Amanda Maire', 'Amandine Aleur', 'Amar Lessirk', 'Ambroise Moygranfou', 'Amour Hirederire', 'Anasthasie Jaineral', 'Anastase Ylokal', 'Anatole Cralien', 'Andrea Litet', 'Andy Capet', 'Andy Vosgembont', 'Ange Oufeu', 'Anne Halle', 'Anne Hurezy', 'Anne Kivive', 'Anne Onyme', 'Anne Oraque', 'Annette Weurk', 'Anne Urezy', 'Annick Passouvant', 'Annick Talope', 'Annie Zette', 'Anny Croche', 'Anny Mateuradio', 'Anny Versert', 'Anselme Hadam', 'Anselme Hatuvent', 'Archy Mandrite', 'Areski Meaux', 'Armand Doline', 'Armande Onorable', 'Armand Talaud', 'Armand Ventelibre', 'Armel Anomme', 'Armelle Apendulaleur', 'Armelle Couvert', 'Arnold Heupe', 'Arthur Adothe', 'Arthur Andot', 'Arthur Demagit', 'Artie Chaud', 'Ashley Menumenu', 'Athanase Broque', 'Aubin Didon', 'Aubin Merdalor', 'Aude Aybussava', 'Aude Alamur', 'Aude Vaisselle', 'Audrey Delock', 'Auguste Dussemeur', 'Augustin Turier', 'Axel Aire', 'Aymard Dianhuite', 'Aziza Continu', 'Balthazar Akolombey', 'Balthazar Messitoyen', 'Barbie Chaite', 'Barbie Turique', 'Bart Aba', 'Benjamin Kukigratte', 'Ben Malaki', 'Bernadette Donneur', 'Bernard Ateur', 'Berthe Blanche', 'Bertrand Donion', 'Betty Poussay', 'Bill Beauquais', 'Blanche Adessin', 'Blanche Debruges', 'Blanche Hapin', 'Blandine Hamite', 'Bob Hinard', 'Bonaparte Manchot', 'Boniface Heurdancre', 'Bruno Cru', 'Bruno Cuit', 'Bruno Zieuvair', 'Calixte Descourses', 'Camille Onciterne', 'Campbell Mabiquette', 'Candy Raton', 'Carlos Amoal', 'Carrie Danter', 'Carry Bansyla', 'Caty Mini', 'Chantal Astarac', 'Chantal Lamesse', 'Charles Atant', 'Charles Magne', 'Chico Rey', 'Claire Fontaine', 'Claire Hettededy', 'Claire Obscur', 'Clara Hoquet', 'Claude Hiquant', 'Clotaire Minusse', 'Cochise Beurgueur', 'Colette Ahailiz', 'Conrad Debreste', 'Daisy Dratet', 'Daisy Meuble', 'Damien Houdarasse', 'Danielle Nimoit', 'Danton Cussal', 'David Cicode', 'Davide Coudevent', 'David Poche', 'David Ordure', 'Debbie Goudy', 'Debbie Scott', 'Debby Zoudanlcou', 'Deborah Diroz', 'Denis Barre', 'Denis Douillet', 'Denis Gokinic', 'Denis Portion', 'Dimitri Postal', 'Dinar Guilet', 'Dino Chandel', 'Dino Zore', 'Djemmal Hojnou', 'Djemal Partou', 'Dominique Henavelo', 'Douglas Alafrez', 'Dom Hinault', 'Doris Faure', 'Dormeur Duval', 'Edith Avuleur', 'Edith Moitu', 'Edith Rice', 'Edmond Dentier', 'Edmond Fissapousset', 'Edmond Taigne', 'Edouard Dewuacance', 'Electre Olize', 'Eleonor Meropehen', 'Elie Coptaire', 'Eliette Etoutaleur', 'Elise Aimoi', 'Elise Yedpore', 'Ella Danloss', 'Elmer Dabloc', 'Elmer Gaize', 'Elmer Hitmieux', 'Elsa Dorsa', 'Elsa Padonf', 'Elsa Persoit', 'Elvira Kedufeux', 'Elvire Debord', 'Elvire Sakuty', 'Elvis Alanvaire', 'Emilie Corne', 'Emily Topessey', 'Emmanuel Skoler', 'Emma Sculey', 'Emma Tomme', 'Enzo Devincenne', 'Eric Azaraille', 'Eric Cochet', 'Estelle Haifone', 'Estelle Urik', 'Eudora Pinfermey', 'Eva Donchier', 'Eva Poret', 'Eva Tican', 'Fabien Malaqui', 'Fabio Loggi', 'Fatima Laya', 'Fellah Manche', 'Fenimore Moilneux', 'Fernand Tassion', 'Fidel Oposte', 'Firmin Dustriel', 'Firmin Haucut', 'Firmin Peutagueul', 'Florent Testinal', 'Florimont Comirespir', 'Francesca Liay', 'Francisca Brel', 'Fred Bouche', 'Freddy Denante', 'Galia Lagerbe', 'Garcin Lazare', 'Gary Guette', 'Gaspard Alyzant', 'Gaston Laplouz', 'Geffrey Benlassiest', 'Geffroy Ausgheg', 'Georges Profonde', 'Georgette Toutenvrac', 'Germaine Eloir', 'Gertrude Bale', 'Gervais Ofrez', 'Gigi Rouette', 'Gibert Raybask', 'Ginette Oilneux', 'Ginette Toiletrou', 'Giovanni Eframboiz', 'Giovanni Zetegras', 'Gladys Deder', 'Gontrand Payte', 'Gontrand Plois', 'Gordon Dessonnett', 'Gordon Zola', 'Gregory Basmathi', 'Guy Bol', 'Guy Dondecourse', 'Guy Liguili', 'Guy Pur', 'Guy Relande', 'Hadil Duchite', 'Hamadi Descrack', 'Hamid Iddis', 'Hank Hulade', 'Hans Chluss', 'Hans Ciclick', 'Hans Hetanlaa', 'Hans Kimkonzern', 'Hans Lipp', 'Harmony Cahensol', 'Haroun Zeuclock', 'Harry Cover', 'Harry Vederchi', 'Harum Desfins', 'Havel Haux', 'Hector Chon', 'Hector Debabel', 'Heidi Sepriaire', 'Helmut Ardemontoney', 'Helmut Stikere', 'Henri Encore', 'Henriette Dumans', 'Henry Bambelle', 'Henry Bouldingue', 'Henry Golo', 'Hercule Avance', 'Hercule Jusqualaporte', 'Hercule Pourkonlenkul', 'Hernanie Sion', 'Hillary Varien', 'Homer Dalors', 'Horace Torrent', 'Hubert Luet', 'Huguette Autroux', 'Humbert Sava', 'Humphrey Biensussey', 'Ignace Ticot', 'Igor Hillanrute', 'Illya Milapine', 'Illya Purienkimamuz', 'Irma Frodite', 'Irma Laya', 'Irma Milecouvert', 'Isadora Lapilule', 'Isidore Miron', 'Jacky Letour', 'Jacky Matunojeux', 'Jade Mirtabite', 'Jacqueline Dezyeux', 'Jacques Roupy', 'Jamel Aussain', 'James Sah', 'James Ucey', 'Jamila Vestancuir', 'Jay Jacule', 'Jean Aihanvi', 'Jean Balsec', 'Jean Bonbeur', 'Jean Bondeparme', 'Jean Bonneau', 'Jean Braye', 'Jean Cive', 'Jean Kulacek', 'Jean Peuplu', 'Jean Saisrien', 'Jean Tanlamer', 'Jeff Epipiolli', 'Jennifer Arpacet', 'Jennifer Riendemain', 'Jerry Kahn', 'Jessica Binet', 'Jessica Pote', 'Jessica Potixel', 'Jessica Trizet', 'Jimmy Maculotalanvair', 'Jimmy Teldindon', 'Joe Bidjoba', 'John Citron', 'John Deuff', 'Jonathan Plurien', 'Jonathan Kettoy', 'Jordan Monly', 'Joseph Duvant', 'Judas Brico', 'Judith Rien', 'Julien Dussand', 'Juste Pourgoutay', 'Justin Instant', 'Justin Pticou', 'Kader Dularge', 'Kader Husselle', 'Karim Aryen', 'Karl Ajumid', 'Karl Amelmoux', 'Kasper Deklak', 'Katia Ourtosukre', 'Kazim Boum', 'Keith Alamess', 'Keith Purlepovre', 'Kelly Diocy', 'Ken Haveau', 'Kent Detoux', 'Kevin Dussenieur', 'Kevin Survin', 'Kimberley Tartine', 'Kim Lamy', 'Klaus Troffob', 'Lance Pierre', 'Larry Golade', 'Lassie Soteuze', 'Lassie Trouille', 'Laura Torio', 'Laure Aidubois', 'Laure Ayencoin', 'Laure Dure', 'Laure Eole', 'Laure Gellay', 'Laurent Barre', 'Laurent Outan', 'Lee Bideau', 'Leilou Lacuisse', 'Lenny Bar', 'Lenny Doizo', 'Leslie Gondolaveniz', 'Leslie Pancuir', 'Levis Serre', 'Linel Ectric', 'Loana Koreth', 'Lola Noyer', 'Louis Dort', 'Louis Fine', 'Louise Kissassoul', 'Louis Kendalamaire', 'Lucas Social', 'Lucie Ametto', 'Lucette Alany', 'Luc Sation', 'Luc Surieux', 'Ludovic Tuaille', 'Ludwig Oureumambre', 'Lukas Kouille', 'Lydie Auduvillage', 'Lydie Comandman', 'Maggie Bolmegratte', 'Maggie Mauve', 'Malcom Unchien', 'Mamadu Zennedeuh', 'Manolito Graffy', 'Manu Militari', 'Marc Assin', 'Marc Depozet', 'Marine Dansonjus', 'Marcella Troutrou', 'Marguerite Fanet', 'Marie Navoile', 'Marie Rouana', 'Marlon Brique', 'Marthe Ellantaite', 'Marty Ney', 'Massoud Abagage', 'Mathias Detet', 'Matt Lekukella', 'Maud Eratheur', 'Maude Issoitil', 'Maurice Tamboule', 'Max Hymum', 'Medhi Teranait', 'Michel Mirezin', 'Mickey Desbrume', 'Mick Robien', 'Mildreed Lox', 'Minnie Mom', 'Mireille Haidelacarte', 'Mireille Levert', 'Mo Bylette', 'Modeste Hinay', 'Modeste Homa', 'Mohamed Alors', 'Mokhtar Kejamey', 'Monica Ragoit', 'Mouloud Maire', 'Moussah Razeh', 'Mousse Line', 'Nadia Rey', 'Nadine Bebeque', 'Nadine Oumouc', 'Narcisse Eydemie', 'Natacha Lumeau', 'Natacha Rivari', 'Nelson Toutebelbelbel', 'Nestor Boyau', 'Nicolas Pessuce', 'Nicolas Rustine', 'Nicole Patonzizi', 'Ninon Nihouy', 'Norad Yroz', 'Nordine Ateur', 'Octave Huleur', 'Odette Dejeux', 'Odette Ritus', 'Odile Atemoilanus', 'Odile Duchite', 'Olaf Herme', 'Olaf Reugeojaux', 'Olga Lopin', 'Olga Luzeau', 'Olive Errapludecito', 'Omar Matuer', 'Omer Cipourtoux', 'Ondine Ahuiteur', 'Ondine Oucesoir', 'Oreste Encorimpeux', 'Oscar Ambar', 'Oscar Fesse', 'Oscar Habosse', 'Oscar Havane', 'Oscar Table', 'Oscar Toffel', 'Othello Bsaidet', 'Otello Dupuis', 'Otto Bus', 'Pamela Mohat', 'Pascal Lagneau', 'Pascal Licot', 'Pascale Sonlont', 'Paterne Auster', 'Patrice Tounet', 'Patricia Dubois', 'Patrick Dane', 'Pat Riote', 'Pat Ronimic', 'Paula Grattet', 'Paulette Bresse', 'Paul Igone', 'Pauline Maginot', 'Paul Nord', 'Paul Ochon', 'Paul Yssemontet', 'Paulo Chon', 'Pedro Signol', 'Pedro Madeire', 'Penny Salamin', 'Petru Dellassecu', 'Petula Danlney', 'Phil Danterre', 'Pierre Hafuzy', 'Pierre Kiroul', 'Pierre Pons', 'Polo Cul', 'Prudence Avantou', 'Quadrat Urducerkl', 'Quang Huru', 'Quasimodo Kini', 'Quasimodo Peyratoire', 'Quennie Tutanblok', 'Quetzalcoatl Havosouhay', 'Quietus Douvientus', 'Quinctius Etiabusse', 'Quincy Danleygogh', 'Quintilianus Boucher', 'Quintilien Conjugo', 'Quirin Saleuille', 'Quirino Faringite', 'Quirinus Hable', 'Qusay Toudroy', 'Qutayba Danlakav', 'Rachid Yendubulbe', 'Ralph Duveldive', 'Raoul Aijeunesse', 'Raoul Dularge', 'Raoul Moizunepel', 'Ramon Moilconduit', 'Raymond Boudif', 'Raymonde Entier', 'Raymond Nomsurlaliste', 'Ray Nette', 'Renaud Cinque', 'Richard Cutry', 'Richard Hognard', 'Rick Hicky', 'Ritchie Partoo', 'Robby Nedochode', 'Robin Didon', 'Robert Hallaire', 'Roger Perdumonfroc', 'Roger Suaf', 'Roger Zujar', 'Roland Mercedez', 'Rosalie Menteyre', 'Rose Daivan', 'Ross Biffe', 'Ruben Aadezijf', 'Rudy Zdedder', 'Ruth Abagah', 'Sabine Lamotte', 'Sabine Lejardin', 'Sacha Huttophon', 'Sacha Sedot', 'Salah Deudeufruy', 'Salah Mi', 'Salima Ongle', 'Salmek Poftip', 'Samantha Lodanzinver', 'Sam Dy', 'Samira Comingan', 'Samira Pazobal', 'Sam Excite', 'Samson Kukomipu', 'Sancho Miz', 'Sandra Sagratte', 'Sarah Bande', 'Sarah Chimpoal', 'Sarah Courci', 'Sarah Frechi', 'Sarah Vigotte', 'Saskia Demieux', 'Saturnin Dejardin', 'Saturnin Peutrovite', 'Scipion Dechek', 'Serge Anchef', 'Serge Houin', 'Sheila Ouate', 'Sheila Lutefinale', 'Sheila Trine', 'Sidney Suzix', 'Sim Kamil', 'Sirah Kashtey', 'Sitiveni Chemoa', 'Solange Gardien', 'Sophie Fonsek', 'Sophie Stickey', 'Stanislav Laqueue', 'Stella Hartois', 'Suzanne Bataid', 'Suzette Lakrep', 'Suzy Zipropre', 'Svetlana Lamoldahaut', 'Sylvain Bouchonnet', 'Sylvie Encortuleux', 'Tabatha Cloison', 'Tahar Tokwetsh', 'Takeshi Danlakol', 'Tatiana Tatianapas', 'Teddy Faurme', 'Thierry Dicule', 'Thomas Ouaque', 'Thomas Teauju', 'Tiburce Plaine', 'Tobbie Hornottoby', 'Tom Ate', 'Tony Gencyl', 'Tony Truand', 'Ulrich Tusse', 'Ulysse Ancieux', 'Urbaine Basculante', 'Urbain Douche', 'Val Degrass', 'Valentine Omic', 'Venceslas Sayssoulier', 'Vic Tim', 'Victoire Alapirus', 'Vincent Timant', 'Vincent Timaitre', 'Violette Argy', 'Virginie Dabeye', 'Vishnou Lapet', 'Vladimir Agecatre', 'Vladimir Guez', 'Wahinuna Vonkedal', 'Waldi Ratamair', 'Walid Tontiquet', 'Walter Boucher', 'Walter Claussette', 'Wally Gator', 'Walt Yplano', 'Wanda Louzy', 'Warren Yepoilu', 'Wayne Hotte', 'Wendy Trez', 'Wenceslas Condit', 'Werter Cervikal', 'Westley Concentrey', 'Whitney Keecool', 'William Jexpire', 'Willy Kuraman', 'Winnie Toutanblok', 'Wladimir Hedlajax', 'Wladimir Pourlawessel', 'Wolf Aktif', 'Xanthippe Atik', 'Xanthos Hamoil', 'Xavier Kafairgaf', 'Yamatata Kishihassi', 'Yann Akpourlui', 'Yanna Pourtous', 'Yannick Etasseur', 'Yannick Toultan', 'Yannis Elnypoivre', 'Yann Niversert', 'Yasser Laidant', 'Yolande Houillette', 'Youkou Lailai', 'Youri Ligotmi', 'Youssouf Danlbalon', 'Yvan Aperth', 'Yvan Sahairdouz', 'Yves Adrouille', 'Yves Atrovite', 'Yves Etrocho', 'Yves Remord', 'Yvette Ferdumal', 'Yvon Enchier', 'Zabou Assandegray', 'Zigfried Handulahr', 'Zinedine Hanville', 'Zita Nesanfiltre', 'Zorba Clava', 'Zorra Dizandemin', 'Zorro Diconduite', 'Zoubida Laire', 'Monseigneur Deport']
grades = ['CM1', 'CM2', '6eme', '5eme']
locations = ['Paris', 'Créteil', 'Versaille', 'Cean']
school = ["Annexe E.N.", "Lucie Aubrac", "Auriacombe", "Georges Bastide 1", "Georges Bastide 2", "Camille Claudel (anciennement Bellefontaine)", "Le Béarnais", "Maurice Bécanne", "Paul Bert", "Étienne Billières", "Bonnefoy", "Borderouge Nord", "Léonce Bourliaguet", "Buffon", "Buissonnière", "Calas", "Château d'Ancely", "Château de l'Hers", "Jean Chaubet", "Courrège", "Pierre et Marie Curie", "Cuvier", "André Daste", "Didier Daurat", "Sylvain Dauriac", "Jean Dieuzaide", "Françoise Dolto", "Armand Duportal", "Gaston Dupouy", "Fabre", "Clément Falcucci", "Falguière", "Daniel Faucher", "Jules Ferry", "Fleurance", "Fontaine Bayonne", "Fontaine Casselardit", "Alain Fournier", "Alexandre Fourtanier", "Anatole France", "Jean Gallia 1", "Jean Gallia 2", "Ginestous", "La Gloire", "Grand Selve", "Henri Guillaumet", "Hameau 47", "Victor Hugo", "Georges Hyon", "Maurice Jacquier", "Jean Jaurès", "Jolimont", "Jules Julien", "La Juncasse", "Lac (École du)", "Léo Lagrange", "Lakanal", "Lamartine", "Lapujade", "Lardenne", "Ferdinand de Lesseps", "Armand Leygue", "Limayrac-Jérôme Pugens", "Littré", "Jean Macé", "La Maourine", "Marengo-Périole", "Marengo-Reille", "Matabiau", "Merly", "Louise Michel", "Michelet", "Michoun A", "Michoun B", "Molière", "Monge", "Jean Monnet", "Montaudran", "Jean Moulin", "Moulis Croix-Bénite", "Alfred de Musset", "Nègreneys", "Niboul", "Les Oustalous", "Papus", "Patte-d'Oie", "Pech David", "Petit Gragnague", "Les Pinhous", "Polygone", "Port Garaud", "Pouvourville", "Rangueil", "Ernest Renan", "Ricardie", "Ronsard", "Saouzelong", "Sarrat", "Sept Deniers", "Hyacinthe Sermet", "Ariane Soupetard", "Tabar", "La Terrasse", "Les Tibaous", "Toec", "Elsa Triolet", "Les Vergers", "Viollet Le Duc"]

def name_generator(names):
    i = 0
    def _generate_name():
        nonlocal i
        name = names[i % len(names)]
        i += 1
        return name
    return _generate_name

generate_name = name_generator(names)

app = Flask(__name__)
api = Api(app)
cors = CORS(app, origin="*")
parser = reqparse.RequestParser()
parser.add_argument('node-name', type=str, help='The name of the the '
                                                'requested nodes')
parser.add_argument('context', type=bool, store_missing=True, help='Does the '
                                                                   'context'
                                                                   'appears '
                                                                   'on node '
                                                                   'parameters')

with open('./data/etab.json') as f:
    etab = json.load(f)
with open('./data/params.json') as f:
    _params = json.load(f)

statements = load_statements(
    '../open-student-environment/data'
    '/statements-brneac3-20180301-20180531'
    '.json')
agents = load_agents(
    '../open-student-environment/data'
    '/accounts-brneac3-0-20180630.json')

env = Environment(agents, statements)
nodes, adjacency = env.nodes, env.structure

active_agents = get_active_agents(statements[:50000])
nodes_filtered = ["804f411c-ecf7-4ba7-b0d9-eb162b8ec1e1",
                  "55db4891-9ea6-4c5d-b55d-2063f815d90d"]
nodes, adjacency = filter_by_users(nodes, adjacency, active_agents)
adjacency = {str(k): v for k, v in adjacency.items()}

etab = [e for e in etab if e['numero_uai'] in nodes]


def create_nodes(adj, nds, func_name,env=env):
    schools = ["Annexe E.N.", "Lucie Aubrac", "Auriacombe", "Georges Bastide 1", "Georges Bastide 2", "Camille Claudel (anciennement Bellefontaine)", "Le Béarnais", "Maurice Bécanne", "Paul Bert", "Étienne Billières", "Bonnefoy", "Borderouge Nord", "Léonce Bourliaguet", "Buffon", "Buissonnière", "Calas", "Château d'Ancely", "Château de l'Hers", "Jean Chaubet", "Courrège", "Pierre et Marie Curie", "Cuvier", "André Daste", "Didier Daurat", "Sylvain Dauriac", "Jean Dieuzaide", "Françoise Dolto", "Armand Duportal", "Gaston Dupouy", "Fabre", "Clément Falcucci", "Falguière", "Daniel Faucher", "Jules Ferry", "Fleurance", "Fontaine Bayonne", "Fontaine Casselardit", "Alain Fournier", "Alexandre Fourtanier", "Anatole France", "Jean Gallia 1", "Jean Gallia 2", "Ginestous", "La Gloire", "Grand Selve", "Henri Guillaumet", "Hameau 47", "Victor Hugo", "Georges Hyon", "Maurice Jacquier", "Jean Jaurès", "Jolimont", "Jules Julien", "La Juncasse", "Lac (École du)", "Léo Lagrange", "Lakanal", "Lamartine", "Lapujade", "Lardenne", "Ferdinand de Lesseps", "Armand Leygue", "Limayrac-Jérôme Pugens", "Littré", "Jean Macé", "La Maourine", "Marengo-Périole", "Marengo-Reille", "Matabiau", "Merly", "Louise Michel", "Michelet", "Michoun A", "Michoun B", "Molière", "Monge", "Jean Monnet", "Montaudran", "Jean Moulin", "Moulis Croix-Bénite", "Alfred de Musset", "Nègreneys", "Niboul", "Les Oustalous", "Papus", "Patte-d'Oie", "Pech David", "Petit Gragnague", "Les Pinhous", "Polygone", "Port Garaud", "Pouvourville", "Rangueil", "Ernest Renan", "Ricardie", "Ronsard", "Saouzelong", "Sarrat", "Sept Deniers", "Hyacinthe Sermet", "Ariane Soupetard", "Tabar", "La Terrasse", "Les Tibaous", "Toec", "Elsa Triolet", "Les Vergers", "Viollet Le Duc"]
    locations = ['Paris', 'Créteil', 'Versaille', 'Cean']
    grades = ['CM1', 'CM2', '6eme', '5eme']
    def generate_school():
        return np.random.choice(schools)
    def generate_grade():
        return np.random.choice(grades)
    def generate_location():
        return np.random.choice(locations)
    def create_node_description(n, typ):
        if typ == 'groupe':
            return {
                'id': str(n),
                'type': typ,
                'name': "groupe {}".format(str(n))
            }
        elif typ == 'classe':
            return {
                'id': str(n),
                'type': typ,
                'name': "classe {}".format(str(n))
            }
        else:
            return {
                'id': str(n),
                'type': typ,
                'name': func_name(),
                'grade': generate_grade(),
                'school': generate_school(),
                'location': generate_location(),
                'indicators':  {"Activite":len(env._statements[str(n)])}
            }

    current_nodes = set()
    nods = []
    for children in adj.values() :
        for n in children :
            if n not in current_nodes:
                current_nodes.add(n)
                nods.append(create_node_description(n, nds[n]))
    for nd in nods:
        if nd['id'] not in adj.keys():
            adj[nd['id']] = []
    adj = {k: list(map(str,list(v))) for k, v in adj.items()}
    return nods, adj

nodes, adjacency = create_nodes(adjacency, nodes, generate_name)

def generate_distrib(n):
    mn = np.random.randint(40, 100)
    std = np.random.randint(10, 20)
    return list(map(np.asscalar, np.random.normal(mn, std,
                                                  n)))

def get_hist(p_val, cont):
    if cont == "discrete":
        t = np.histogram(p_val, bins=1000)
    else:
        t = np.histogram(p_val, bins=1000, density=True)
    return {'values': list(map(np.asscalar, list(t[0]))),
            'bins': list(map(np.asscalar, list(t[1])))}

node_params = defaultdict(dict)
params_dist = {k: {'dist': list(generate_distrib(len(nodes)))} for k in
               _params.keys()}

for p_key, p_val in params_dist.items():
    params_dist[p_key]['hist'] = get_hist(p_val['dist'], _params[p_key])
    params_dist[p_key]['max'] = max(p_val['dist'])
    params_dist[p_key]['min'] = min(p_val['dist'])
    assign = np.random.choice(p_val['dist'], len(nodes), replace=False)
    del (params_dist[p_key]['dist'])
    for a, n in enumerate(nodes):
        if n['type'] != 'groupe' and n['type'] != 'classe' :
            n['indicators'][p_key] = assign[a]

class GetParametersNames(Resource):
    def get(self):
        return list(params_dist.keys())


class GetNodes(Resource):
    def get(self):
        return nodes


class GetAdjancy(Resource):
    def get(self):
        return adjacency


class GetEtab(Resource):
    def get(self):
        return etab


def get_format(name, params):
    def create_dict(a, b):
        return {'name': a, 'value': b}

    resp = {}
    resp['name'] = name
    resp['type'] = _params[name]
    resp['series'] = [create_dict(a, b) for a, b in zip(params['hist']['bins'],
                                                        params[
                                                            'hist'][
                                                            'values'])]
    return resp


class GetPamaters(Resource):
    def get(self):
        resp = [get_format(k, v) for k, v in params_dist.items()]
        return resp


def get_formatted_params(name, params):
    resp = {'name': name,
            'value': params['value']
            }
    return resp


class GetNodeParameters(Resource):
    def get(self):
        args = parser.parse_args()
        resp = {}
        if args['context']:
            resp['context'] = [get_format(k, v) for k, v in
                               params_dist.items()]
        if node_params[args['node-name']]:
            resp['name'] = 'node-parameters'
            resp['series'] = [get_formatted_params(k, p) for k, p in
                              node_params[args['node-name']].items()]
        return resp


def convert_timestamp_to_datetime(activity):
    if activity is None:
        return None
    if type(activity['timestamp']) != str:
        activity['timestamp'] = datetime.datetime.utcfromtimestamp(activity[
                                                                       'timestamp']
                                                                   ).strftime(
            '%Y-%m-%d %H:%M:%S')
    return activity


def convert_timestamp_to_datetime_formatted(activity):
    if activity is None:
        return None
    if type(activity['timestamp']) != str:
        activity['timestamp'] = datetime.datetime.utcfromtimestamp(activity[
                                                                       'timestamp']
                                                                   ).strftime(
            '%Y-%m-%d %H:%M:%S')
    return activity['timestamp']


class GetNodeActivityFormatted(Resource):
    def get(self):
        args = parser.parse_args()
        x = list(map(convert_timestamp_to_datetime,
                     env._statements[args['node-name']]))
        y = len(x) * [1]
        resp = {'x': x,
                'y': y,
                'type': 'scatter'}
        return resp


class GetNodeActivity(Resource):
    def get(self):
        args = parser.parse_args()
        return list(map(convert_timestamp_to_datetime,
                        env._statements[args['node-name']]))


api.add_resource(GetNodes, '/nodes')
api.add_resource(GetAdjancy, '/adjancy')
api.add_resource(GetEtab, '/etab')
api.add_resource(GetParametersNames, '/model')
api.add_resource(GetPamaters, '/model/parameters')
api.add_resource(GetNodeParameters, '/nodes/parameters')
api.add_resource(GetNodeActivity, '/nodes/activity')

if __name__ == '__main__':
    app.run(debug=True)
