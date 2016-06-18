from datetime import datetime as DT, timedelta
import glob
import gzip
import os


def archive_files():
    """
    This will loop through all assigned directories and extensions to zip up
    and archive any folders older than yesterday
    """
    # TODO: Add a configuration file for these variables
    archive_dir_list = ['Logs']
    archive_extension_list = ['.log']
    archive_path = 'Logs\\Archive'
    archive_days_to_save = 7

    # log = logger.build_logger(name='archiver', level='INFO')
    # log.set_step('archive files')
    #
    # log.info('Directories to archive: {}'.format(archive_dir_list))
    # log.info('Extensions to archive: {}'.format(archive_extension_list))

    if not os.path.isdir(archive_path):
        os.mkdir(archive_path)

    date_format = '%Y%m%d'
    date = DT.now().strftime(date_format)
    yesterday_time = ((DT.strptime(date, date_format)) - timedelta(1)).strftime(date_format)
    oldest_log_date = ((DT.strptime(date, date_format)) - timedelta(archive_days_to_save)).strftime(date_format)

    for directory in archive_dir_list:
        full_path = os.path.join(os.getcwd(), directory)
        for file_extension in archive_extension_list:
            for this_file in glob.glob(os.path.join(full_path, '*.{}'.format(file_extension))):
                file_mod_time = DT.fromtimestamp(os.path.getmtime(this_file)).strftime(date_format)
                if file_mod_time <= yesterday_time:
                    file_name = os.path.basename(this_file)
                    # log.info('Found existing file to be archived: {}'.format(file_name))
                    new_path = archive_path + '\\' + file_name
                    infile = open(this_file, 'r')
                    outfile = gzip.open('{}.gz'.format(new_path), 'w')
                    outfile.writelines(infile)
                    infile.close()
                    outfile.close()
                    os.remove(this_file)
                    # log.info('File {} successfully archived'.format(file_name))

    # log.info('Cleaning up old outputs, removing anything older than {} days'.format(archive_days_to_save))

    for this_file in os.listdir(archive_path):
        path_name = os.path.join(archive_path, this_file)
        file_mod_time = DT.fromtimestamp(os.path.getmtime(path_name)).strftime(date_format)
        if file_mod_time <= oldest_log_date:
            # log.info('Removing {}'.format(path_name))
            os.remove(path_name)
