import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
from common.db_IO import Connection
import common.functions as functions
from common.heredicare_interface import Heredicare
import frontend_celery.webapp.tasks as tasks
from webapp.download.download_routes import calculate_class

def print_progress_bar(iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

class PRIV_Connection(Connection):
    def update_user_classification_based_on_selected_criteria(self, user_classification_id, classification):
        command = "UPDATE user_classification SET scheme_class = %s WHERE id = %s"
        self.cursor.execute(command, (str(classification), user_classification_id))
        self.conn.commit()

    def update_consensus_classification_based_on_selected_criteria(self, consensus_classification_id, classification):
        command = "UPDATE consensus_classification SET scheme_class = %s WHERE id = %s"
        self.cursor.execute(command, (str(classification), consensus_classification_id))
        self.conn.commit()



conn = PRIV_Connection(roles = ["super_user"])

logfile=open("update_classification.log", "w")

variant_ids = conn.get_all_valid_variant_ids()
#variant_ids = [35118]
print_progress_bar(0, len(variant_ids), prefix = 'Progress:', suffix = 'Complete', length = 50)

scheme_dict = {}
classification_schemes = conn.get_all_classification_schemes()
for classification_scheme in classification_schemes:
    scheme_id = classification_scheme.id
    result = conn.get_classification_scheme(scheme_id) # id,name,display_name,type,reference,is_active,is_default,version

    scheme_dict[scheme_id] = {
        "type": result[3],
        "version": result[7]
    } 


for i, variant_id in enumerate(variant_ids):

    variant = conn.get_variant(variant_id,
        include_annotations = False, 
        include_consensus = True, 
        include_user_classifications = True, 
        include_heredicare_classifications = False, 
        include_automatic_classification = False,
        include_clinvar = False, 
        include_consequences = False, 
        include_assays = False, 
        include_literature = False,
        include_external_ids = False
    )


    if variant.user_classifications is not None:
        for classification in variant.user_classifications:
            all_criteria_strengths = []

            scheme = scheme_dict[classification.scheme.id]
            scheme_type = scheme["type"]
            scheme_version = scheme["version"]

            for criterion in conn.get_scheme_criteria_applied(classification.id, where = "user"):
                # id
                # user/consensus_classification_id
                # classification_criterium_id
                # criterium_strength_id
                # evidence
                # classification_criterium_name
                # classification_criterium_strength_name
                # classification_criterium_strength.description
                # classification_criterium_strength.display_name
                # y.state
                if criterion[9] == "selected":
                    if criterion[5] == "BP1" and scheme_type in ["acmg-enigma-brca1", "acmg-enigma-brca2"]:
                        all_criteria_strengths.append( criterion[5] + '_' + criterion[6])
                    elif  criterion[5] == "PM2" and scheme_type in ["acmg-enigma-atm"]:
                        all_criteria_strengths.append( criterion[5] + '_' + criterion[6])
                    elif  criterion[5] == "PVS1" and scheme_type in ["acmg-enigma-atm"]:
                        all_criteria_strengths.append( criterion[5] + '_' + criterion[6])
                    else:
                        all_criteria_strengths.append(criterion[6])
            all_criteria_string = '+'.join(all_criteria_strengths)

            if all_criteria_string != "":
                classification_dict = calculate_class(scheme_type, scheme_version, all_criteria_string)
                scheme_class = classification_dict["final_class"]
            elif scheme_type == "none":
                scheme_class = "-"
            else:
                scheme_class = 3

            if str(classification.scheme.selected_class) != str(scheme_class):
                logfile.write("updated user classification: " + str(variant.id) + " from " + str(classification.scheme.selected_class) + " to " + str(scheme_class) + "\n")

                conn.update_user_classification_based_on_selected_criteria(
                    classification.id,
                    scheme_class
                )


    if variant.consensus_classifications is not None:
        for classification in variant.consensus_classifications:
            all_criteria_strengths = []

            scheme = scheme_dict[classification.scheme.id]
            scheme_type = scheme["type"]
            scheme_version = scheme["version"]

            for criterion in conn.get_scheme_criteria_applied(classification.id, where = "consensus"):
                # id
                # user/consensus_classification_id
                # classification_criterium_id
                # criterium_strength_id
                # evidence
                # classification_criterium_name
                # classification_criterium_strength_name
                # classification_criterium_strength.description
                # classification_criterium_strength.display_name
                # y.state
                if criterion[9] == "selected":
                    if criterion[5] == "BP1" and scheme_type in ["acmg-enigma-brca1", "acmg-enigma-brca2"]:
                        all_criteria_strengths.append( criterion[5] + '_' + criterion[6])
                    elif  criterion[5] == "PM2" and scheme_type in ["acmg-enigma-atm"]:
                        all_criteria_strengths.append( criterion[5] + '_' + criterion[6])
                    elif  criterion[5] == "PVS1" and scheme_type in ["acmg-enigma-atm"]:
                        all_criteria_strengths.append( criterion[5] + '_' + criterion[6])
                    else:
                        all_criteria_strengths.append(criterion[6])
            all_criteria_string = '+'.join(all_criteria_strengths)

            if all_criteria_string != "":
                classification_dict = calculate_class(scheme_type, scheme_version, all_criteria_string)
                scheme_class = classification_dict["final_class"]
            elif scheme_type == "none":
                scheme_class = "-"
            else:
                scheme_class = 3

            if str(classification.scheme.selected_class) != str(scheme_class):
                logfile.write("updated consensus classification: " + str(variant.id) + " from " + str(classification.scheme.selected_class) + " to " + str(scheme_class) + "\n")

                conn.update_consensus_classification_based_on_selected_criteria(
                    classification.id,
                    scheme_class
                )



    print_progress_bar(i+1, len(variant_ids), prefix = 'Progress:', suffix = 'Complete', length = 50)




conn.close()

