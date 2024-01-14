import argparse
import json

from actions.cliq_action import CliqAction
from cliq_properties import CliqProperties


class Predict(CliqAction):
    def __init__(self, aa: argparse.ArgumentParser):
        super().__init__("predict")

        p = aa.add_parser(
            self.name, help="uses a data file to predict the dictionary and mapping"
        )
        CliqAction._add_file_arg(p)
        CliqAction._add_output_arg(p)

    def run(self, opts: argparse.Namespace, props: CliqProperties):
        # SDZ ADMIN
        gc = CliqAction._get_sdz_admin(props)
        dictionary, mapping = gc.predict(opts.file)

        if opts.output is None:
            print(f"dictionary:\n{json.dumps(dictionary, indent=2)}")
            print(f"mapping:\n{json.dumps(mapping, indent=2)}")
        else:
            print(f"saving dictionary and mapping files: {opts.output}/{opts.name}*")

            with open(f"{opts.output}/{opts.name}_dict.json", "wt") as f:
                json.dump(dictionary, f, indent=2)

            with open(f"{opts.output}/{opts.name}_mapping.json", "wt") as f:
                json.dump(mapping, f, indent=2)
