#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
"""
import argparse
import logging
import wandb
import pandas as pd


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    # artifact_local_path = run.use_artifact(args.input_artifact).file()

    logger.info("Downloading and reading input artifact")
    artifact_local_path = run.use_artifact(args.input_artifact).file()

    df = pd.read_csv(artifact_local_path)


    logger.info("Dropping outliers")
    min_price = args.min_price
    max_price = args.max_price
    idx = df['price'].between(min_price, max_price)
    df = df[idx].copy()

    logger.info("Converting last_review to datetime")
    df['last_review'] = pd.to_datetime(df['last_review'])

    df.to_csv("clean_sample.csv", index=False)

    logger.info("Uploading artifact to W&B")
    artifact = wandb.Artifact(
        args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )
    artifact.add_file("clean_sample.csv")
    run.log_artifact(artifact)

    logger.info("Data cleaning process completed")




if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")


    parser.add_argument(
        "--input_artifact",
        type= str,
        help= "Name of the artifact data to be cleaned",
        required=True
    )

    parser.add_argument(
        "--output_artifact",
        type= str,
        help= "Name of the output artifact with cleaned data",
        required=True
    )

    parser.add_argument(
        "--output_type",
        type= str,
        help="Type of the output artifact",
        required=True
    )

    parser.add_argument(
        "--output_description",
        type= str,
        help="Description of the cleaned dataset",
        required=True
    )

    parser.add_argument(
        "--min_price",
        type= float,
        help="Lower limit of acceptable prices",
        required=True
    )

    parser.add_argument(
        "--max_price",
        type= float,
        help="Upper limit of acceptable prices",
        required=True
    )


    args = parser.parse_args()

    go(args)
