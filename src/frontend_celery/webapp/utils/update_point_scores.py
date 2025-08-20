import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
from common.db_IO import Connection
import common.functions as functions
from common.heredicare_interface import Heredicare
import frontend_celery.webapp.tasks as tasks
from webapp.download.download_routes import calculate_point_score

def print_progress_bar(iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

class PRIV_Connection(Connection):
    def update_point_score_user(self, user_classification_id, point_score, point_class):
        command = "UPDATE user_classification SET point_score = %s, point_class = %s WHERE id = %s"
        self.cursor.execute(command, (point_score, str(point_class), user_classification_id))
        self.conn.commit()

    def update_point_score_consensus(self, user_classification_id, point_score, point_class):
        command = "UPDATE consensus_classification SET point_score = %s, point_class = %s WHERE id = %s"
        self.cursor.execute(command, (point_score, str(point_class), user_classification_id))
        self.conn.commit()


conn = PRIV_Connection(roles = ["super_user"])


variant_ids = conn.get_all_valid_variant_ids()
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
            for criterion in conn.get_scheme_criteria_applied(classification.id, where = "user"):
                if criterion[9] == "selected":
                    all_criteria_strengths.append(criterion[6])
            all_criteria_string = '+'.join(all_criteria_strengths)

            if all_criteria_string != "":
                scheme = scheme_dict[classification.scheme.id]
                scheme_type = scheme["type"]
                scheme_version = scheme["version"]

                point_classification_dict = calculate_point_score(scheme_type, scheme_version, all_criteria_string)
                point_class = point_classification_dict["classification"]
                point_score = point_classification_dict["points"]
            else:
                point_score = 0
                point_class = "3"

            conn.update_point_score_user(
                classification.id,
                point_score, 
                point_class
            )


    if variant.consensus_classifications is not None:
        for classification in variant.consensus_classifications:
            all_criteria_strengths = []
            for criterion in conn.get_scheme_criteria_applied(classification.id, where = "consensus"):
                if criterion[9] == "selected":
                    all_criteria_strengths.append(criterion[6])
            all_criteria_string = '+'.join(all_criteria_strengths)

            if all_criteria_string != "":
                scheme = scheme_dict[classification.scheme.id]
                scheme_type = scheme["type"]
                scheme_version = scheme["version"]

                point_classification_dict = calculate_point_score(scheme_type, scheme_version, all_criteria_string)
                point_class = point_classification_dict["classification"]
                point_score = point_classification_dict["points"]
            else:
                point_score = 0
                point_class = "3"

            conn.update_point_score_consensus(
                classification.id,
                point_score, 
                point_class
            )

    print_progress_bar(i+1, len(variant_ids), prefix = 'Progress:', suffix = 'Complete', length = 50)




conn.close()

