from network_security.aws import s3_syncer

if __name__ == '__main__':
    s3_syncer.upload_folder_to_s3("artifacts", s3_prefix="artifacts")
    s3_syncer.upload_folder_to_s3("final_model", skip_if_exists=False, s3_prefix="final_model")