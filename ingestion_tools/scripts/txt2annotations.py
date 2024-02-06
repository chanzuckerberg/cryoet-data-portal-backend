#!/usr/bin/env python3
import csv

import click
import dateparser
import ndjson
import starfile


@click.group()
@click.pass_context
def cli(ctx):
    pass


@cli.command(name="convert-csv")
@click.argument("csvfilename", required=True, type=str)  # TODO - use click types
@click.argument("molecule", required=True, type=str)
@click.argument("annotator", required=True, type=str)
@click.argument("annotation_date", required=True, type=str)
@click.pass_context
def convert_csv(ctx, csvfilename: str, molecule: str, annotator: str, annotation_date: str):
    with open(csvfilename, "r") as data:
        points = csv.reader(data, delimiter=",")
    output_data = []
    for coord in points:
        output_data.append(
            {
                "annotationShape": {
                    "type": "point",
                    "location": {"x": coord[0], "y": coord[1], "z": coord[2]},
                },
                "molecule": molecule,
                "organelle": None,
                "annotator": annotator,
                "annotationDate": dateparser.parse(annotation_date).isoformat(),
            },
        )
    print(ndjson.dumps(output_data))


@cli.command(name="convert-star")
@click.argument("starfilename", required=True, type=str)
@click.argument("molecule", required=True, type=str)
@click.argument("annotator", required=True, type=str)
@click.argument("annotation_date", required=True, type=str)
@click.pass_context
def convert_star(ctx, starfilename: str, molecule: str, annotator: str, annotation_date: str):
    df = starfile.read(starfilename)
    output_data = []
    for _, coord in df.iterrows():
        output_data.append(
            {
                "annotationShape": {
                    "type": "orientedPoint",
                    "location": {
                        "x": coord["rlnCoordinateX"],
                        "y": coord["rlnCoordinateY"],
                        "z": coord["rlnCoordinateZ"],
                    },
                    "orientation": {
                        "rot": coord["rlnAngleRot"],
                        "tilt": coord["rlnAngleTilt"],
                        "psi": coord["rlnAnglePsi"],
                    },
                },
                "molecule": molecule,
                "organelle": None,
                "annotator": annotator,
                "annotationDate": dateparser.parse(annotation_date).isoformat(),
            },
        )
    print(ndjson.dumps(output_data))


if __name__ == "__main__":
    cli()
