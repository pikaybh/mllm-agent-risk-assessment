import os
import inspect
import logging
from datetime import datetime
from typing import Optional


class LoggerSetup:
    """
    A utility class for setting up a logger with file rotation and stream handling.

    Attributes:
        logger_name (str): The name of the logger, defaults to the caller's module name.
        log_dir (str): The directory where log files will be stored.
        log_date (str): The current date in 'YYYY-MM-DD-Day' format.
        log_file (str): The full path to the current log file.
        MAX_LOG_SIZE (int): The maximum size of a log file in bytes.
        BACKUP_COUNT (int): The maximum number of backup log files to keep.

    Methods:
        logger: Returns the logger instance.
        max_log_size: Gets or sets the maximum log file size based on a size factor.
        setup_logger(): Sets up the logger with file and stream handlers.
    """

    def __init__(self, logger_name: Optional[str] = None, log_size_factor: float = 0.8):
        """
        Initializes a LoggerSetup instance.

        Args:
            logger_name (Optional[str]): The name of the logger. Defaults to the caller's module name.
            log_size_factor (float): A factor (0.0 < factor <= 1.0) to determine the maximum log file size
                                     based on GitHub's maximum upload size (100MB). Defaults to 0.8.

        Raises:
            ValueError: If log_size_factor is not between 0.0 and 1.0.
        """
        self.logger_name = logger_name or self._get_caller_name()
        self._logger = logging.getLogger(self.logger_name)
        self._logger.setLevel(logging.DEBUG)
        self.log_dir = f'logs/{self.logger_name}'
        self.log_date = datetime.now().strftime('%Y-%m-%d-%a')  # Format: YYYY-MM-DD-Day
        self.log_file = f"{self.log_dir}/{self.log_date}.log"

        # Default log size setting (80% of GitHub max upload size)
        self.MAX_LOG_SIZE = self._calculate_max_log_size(log_size_factor)
        self.BACKUP_COUNT = 5  # Max backup files

        # Prepare log directory and set up logger
        self._prepare_log_directory()
        self.setup_logger()

    def _get_caller_name(self) -> str:
        """
        Gets the name of the calling module.

        Returns:
            str: The name of the calling module.
        """
        return inspect.stack()[2].frame.f_globals["__name__"]

    def _prepare_log_directory(self):
        """
        Creates the log directory if it does not already exist.
        """
        os.makedirs(self.log_dir, exist_ok=True)

    def _calculate_max_log_size(self, factor: float) -> int:
        """
        Calculates the maximum log file size.

        Args:
            factor (float): A factor to determine the maximum size (0.0 < factor <= 1.0).

        Returns:
            int: The maximum log size in bytes.

        Raises:
            ValueError: If factor is not between 0.0 and 1.0.
        """
        if not (0.0 < factor <= 1.0):
            raise ValueError(f"factor should be between 0 and 1 (given: {factor})")
        return int(100 * 1_024 * 1_024 * factor)

    @property
    def logger(self) -> logging.Logger:
        """
        Gets the logger instance.

        Returns:
            logging.Logger: The logger instance.
        """
        return self._logger

    @property
    def max_log_size(self) -> int:
        """
        Gets the maximum log size.

        Returns:
            int: The maximum log size in bytes.
        """
        return self.MAX_LOG_SIZE

    @max_log_size.setter
    def max_log_size(self, factor: float) -> None:
        """
        Sets the maximum log size.

        Args:
            factor (float): A factor to determine the maximum size (0.0 < factor <= 1.0).

        Raises:
            ValueError: If factor is not between 0.0 and 1.0.
        """
        self.MAX_LOG_SIZE = self._calculate_max_log_size(factor)

    def _create_file_handler(self) -> logging.FileHandler:
        """
        Creates a file handler for logging with rollover support.

        Returns:
            logging.FileHandler: The configured file handler.
        """
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8-sig')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter(r'%(asctime)s [%(name)s, line %(lineno)d] %(levelname)s: %(message)s')
        )
        file_handler.emit = self._file_emit_with_rollover(file_handler)
        return file_handler

    def _file_emit_with_rollover(self, handler: logging.FileHandler):
        """
        Wraps the emit function to handle file size rollover.

        Args:
            handler (logging.FileHandler): The file handler to wrap.

        Returns:
            Callable: A wrapped emit function with rollover support.
        """
        def emit(record):
            if os.path.exists(handler.baseFilename) and os.path.getsize(handler.baseFilename) >= self.MAX_LOG_SIZE:
                self._do_rollover(handler)
            logging.FileHandler.emit(handler, record)
        return emit

    def _do_rollover(self, handler: logging.FileHandler):
        """
        Performs a log file rollover.

        Args:
            handler (logging.FileHandler): The file handler for which rollover is performed.
        """
        handler.close()
        for i in range(self.BACKUP_COUNT - 1, 0, -1):
            sfn = f"{self.log_file}.{i}"
            dfn = f"{self.log_file}.{i + 1}"
            if os.path.exists(sfn):
                if os.path.exists(dfn):
                    os.remove(dfn)
                os.rename(sfn, dfn)

        dfn = f"{self.log_file}.1"
        if os.path.exists(self.log_file):
            os.rename(self.log_file, dfn)

        handler.stream = handler._open()

    def _create_stream_handler(self) -> logging.StreamHandler:
        """
        Creates a stream handler for logging.

        Returns:
            logging.StreamHandler: The configured stream handler.
        """
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(logging.Formatter(r'%(message)s'))
        return stream_handler

    def setup_logger(self):
        """
        Sets up the logger with file and stream handlers.
        """
        file_handler = self._create_file_handler()
        stream_handler = self._create_stream_handler()

        self._logger.addHandler(file_handler)
        self._logger.addHandler(stream_handler)
