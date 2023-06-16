from rdflib import Namespace
from rdflib import Graph
from rdflib.namespace import RDF
from rdflib.namespace import Namespace
from rdflib import URIRef, BNode, Literal
from rdflib import Graph, Literal, Namespace, RDF, RDFS, XSD
from rdflib.namespace import FOAF
import itertools
import pandas as pd   
import time
import csv
import ast
import time
from datetime import datetime

fho = Namespace("http://purl.org/ontology/fho/")
mpo = Namespace('http://purl.org/ontology/mpo/')
g = Graph()

nx = fho.hasNext
pr = fho.hasPrevious

is_first_track_chord = mpo.isFirstTrackChordof
is_last_track_chord = mpo.isLastTrackChordof
nx_part = mpo.hasNextPart
has_first_part_chord = mpo.hasFirstPartChord
has_last_part_chord = mpo.hasLastPartChord
has_part_chord = mpo.hasPartChord
has_part = mpo.hasPart
has_release = mpo.hasReleaseDate

has_chord_progression = mpo.hasChordProgression
has_first_prog_chord = mpo.hasFirstProgChord
has_last_prog_chord = mpo.hasLastProgChord
has_chord_count = mpo.hasChordCount
has_prog_chord = mpo.hasProgChord

has_next_progression = mpo.hasNextChordProgression
has_genre = mpo.hasGenre

class_track = mpo.Track
class_chord = mpo.Chord
class_part = mpo.Part
class_progression = mpo.ChordProgression


tracks = pd.read_csv('final_changed_parts.csv')

ids = tracks['id'].tolist()
progressions = tracks['chord_progression'].tolist()
genres = tracks['genre'].tolist()
dates = tracks['release_date'].tolist()



def hasNext_function(track,track_chord_progression, OntoProperty, OntoFirst, OntoLast, g):
    chord_count = {}
    prev_chord = None
    for i, chord in enumerate(track_chord_progression):
        if chord not in chord_count:
            chord_count[chord] = 1
        else:
            chord_count[chord] += 1
        if (i == 0) and (OntoFirst is not None):
           
            g.add((chord, OntoFirst, track))
        if (i == len(track_chord_progression) - 1) and (OntoLast is not None):
           
            g.add((chord, OntoLast, track))

        if prev_chord is not None:
            
            g.add((prev_chord, OntoProperty, chord))
        
        prev_chord = chord

def hasFirstandLast_function(track_dict, OntoFirst, OntoLast, OntoChord,g):
    for key in track_dict:
        value_list = track_dict[key]
        if len(value_list) > 1:
            first_element = value_list[0]
            last_element = value_list[1]
        else:
            first_element = value_list[0]
            last_element = value_list[0]
        
        g.add((key, OntoFirst, first_element))
        g.add((key, OntoLast, last_element))
        for j in value_list:
            
            g.add((key,OntoChord,j))

def findChordProgressions(part_instance,elements, part_name, OntoPart, OntoFirst, OntoLast, OntoCounting, OntoChord, min_length, max_length,g, id):
    combinations = []
    unique_combinations = []
    chord_progression_instances = []
    counting = {}
    c = 1
    for length in range(min_length, min(max_length + 1, len(elements) + 1)):
        for i in range(len(elements) - length + 1):
            current_combination = elements[i:i+length]
            is_unique = True

            for existing_combination in unique_combinations:
                if (all(item in existing_combination for item in current_combination)) and (len(existing_combination)!= len(current_combination)):
                    is_unique = False
                    break

            if is_unique:
                unique_combinations.append(current_combination)
                
                progression_instance = mpo[f"{str(genres[id]) + '_'+ str(ids[id])}_{part_name}_{'ChordProgression'}_{c}"]
                g.add((progression_instance, RDF.type, class_progression))
                chord_progression_instances.append(progression_instance)
                c +=1
               
                g.add((part_instance, OntoPart, progression_instance))
                first_element = current_combination[0]
                last_element = current_combination[-1]
               
                g.add((progression_instance, OntoFirst, first_element))
                g.add((progression_instance, OntoLast, last_element))
                for j in current_combination:
                    
                    g.add((progression_instance, OntoChord,j))
                chord_count = 0
                for j in current_combination:
                    chord_count += 1
              
                # Convert the integer to a Literal object
                chord_count_literal = Literal(chord_count)
                g.add((progression_instance, OntoCounting, chord_count_literal))
                counting[progression_instance] = chord_count

    
  
    for i in chord_progression_instances:
        combinations.append((i,counting[i]))
    return combinations

start_time = time.time()

for i in range(2):
    if i % 10 == 0:
        print(i)
    if i % 100 == 0:
        c_time = time.time()
        print(f"Elapsed time: {c_time-start_time:.2f} seconds")
        print(f"Estimated time: {(c_time-start_time)/(i+1)*77000:.2f} seconds")
    g = Graph()
    b = 0 #chord counter
    string_with_brackets = progressions[i]
    string_without_brackets = string_with_brackets.replace("[", "").replace("]", "")  # Step 1
    string_without_quotes = string_without_brackets.replace("'", "")  # Step 2
    final_string = string_without_quotes.replace(", ", " ")  # Step 3
    track_list = final_string.split()

    track_dict = {}
    current_key = None
    current_value = []

    # define instances!!!!!
    track_instance = mpo[str(genres[i]) + '_'+ str(ids[i])]
    g.add((track_instance, RDF.type, class_track))
    genre_instance = mpo[str(genres[i]).capitalize()]
    g.add((track_instance, has_genre, genre_instance))
    date_string = dates[i]
    if len(date_string) == 4:
        date_object = Literal(date_string, datatype=XSD.datetime)
    elif len(date_string) == 7:
        date_object = Literal(date_string, datatype=XSD.datetime)
    else:
        date_object = Literal(date_string, datatype=XSD.datetime)
    # date_instance = Literal(date_object, datatype=XSD.datetime)
    g.add((track_instance, has_release, date_object))
    chord_count = {}
    part_count = {}
    dummy_part = ''
    for part in track_list:
       
        if part.startswith('<'):
            new_part = part.replace('<','').replace('>','')
            if part not in part_count:
                part_count[part] = 1
            else:
                part_count[part] += 1
            if current_key is not None:
                track_dict[current_key] = current_value
            part_instance = mpo[f"{str(genres[i]) + '_'+ str(ids[i])}_{new_part}"]
            part_class = mpo[new_part.split("_")[0].capitalize()]
            g.add((part_instance, RDF.type, part_class))
            g.add((track_instance, mpo['has'+new_part.split("_")[0].capitalize()], part_instance))
            current_key = part_instance
            current_value = []
            dummy_part = part
        else:
            if part != dummy_part:
                if part not in chord_count:
                    chord_count[part] = 1
                else:
                    chord_count[part] += 1
                b +=1 
                part_instance = mpo[f"{str(genres[i]) + '_'+ str(ids[i])}_{part}_{b}"]
                part_class = fho[part]
                g.add((part_instance, RDF.type, part_class))
                current_value.append(part_instance)
                dummy_part = part

    if current_key is not None:
        track_dict[current_key] = current_value
    
    track_chord_progression = []
    for value_list in track_dict.values():
        track_chord_progression.extend(value_list)

    hasNext_function(track_instance,track_chord_progression, nx, is_first_track_chord, is_last_track_chord, g )
    hasNext_function(track_instance,track_dict.keys(), nx_part, None, None,g)
    hasFirstandLast_function(track_dict, has_first_part_chord, has_last_part_chord, has_part_chord,g)
    full_chord_progression_instances = []
    for part in track_dict:
        chords = track_dict[part]
        part_str = str(part)
        part_str_split = part_str.split('_')
        part_name = part_str_split[-2] + '_' + part_str_split[-1]
        chord_progression_instances = findChordProgressions(part, chords, part_name, has_chord_progression, has_first_prog_chord, has_last_prog_chord,has_chord_count,has_prog_chord, 3, 8, g, i)
        full_chord_progression_instances.append(chord_progression_instances)

    new_list = list(itertools.chain(*full_chord_progression_instances))
    for prog in range(len(new_list)-1):
        
        counter = new_list[prog][1]
        if ((prog+counter) < len(new_list)) and (new_list[prog+counter][1] == counter):
      
            g.add((new_list[prog][0], has_next_progression, new_list[prog+1][0]))



    g.serialize(destination='destination '.owl', format='xml')
   
