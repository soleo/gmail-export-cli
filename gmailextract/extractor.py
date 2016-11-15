import os
import pygmail.errors
from .fs import sanatize_filename, unique_filename
from pygmail.account import Account

ATTACHMENT_MIMES = ('image/jpeg', 'image/png', 'image/gif', 'application/pdf', 'application/octet-stream')

class GmailExtractor(object):
    """gmail extrating class which handles connecting to gmail on behalf of
    a user over IMAP, extracts attachements from messages in a Gmail account,
    writes them to disk
    """

    def __init__(self, dest, email, password, limit=None, batch=10):
        """
        Args:
            dest     -- the path on the file system where images should be
                        extracted and written to.
            email -- the username of the Gmail account to connect to
            password -- the password of the Gmail account to connect to

        Keyword Args:
            limit   -- an optional limit of the total number of messages to
                       download from the gmail account.
            batch   -- the maximum number of messages to download from Gmail
                       at the same time.
           

        raise:
            ValueError -- If the given dest path to write extracted images to
                          is not writeable.
        """
        self.dest = dest

        if not self.validate_path():
            raise ValueError("{0} is not a writeable directory".format(dest))

        if 'attachments' not in os.listdir(self.dest):
            os.mkdir('attachments')
            self.dest = dest + '/attachments'

        self.limit = limit
        self.batch = batch
        self.email = email
        self.password = password

    def validate_path(self):
        """Checks to see the currently selected destiation path, for where
        extracted images should be written, is a valid path that we can
        read and write from.

        Return:
            A boolean description of whether the currently selected destination
            is a valid path we can read from and write to.
        """
        if not os.path.isdir(self.dest):
            return False
        elif not os.access(self.dest, os.W_OK):
            return False
        else:
            return True

    def connect(self):
        """Attempts to connect to Gmail using the username and password provided
        at instantiation.

        Returns:
            Returns a boolean description of whether we were able to connect
            to Gmail using the current parameters.
        """
        mail = Account(self.email, password=self.password)

        trash_folder = mail.trash_mailbox()
        if pygmail.errors.is_error(trash_folder):
            return False
        else:
            self.mail = mail
            self.trash_folder = trash_folder
            self.inbox = mail.all_mailbox()
            return True

    def num_messages_with_attachments(self):
        """Checks to see how many Gmail messages have attachments in the
        currently connected gmail account.

        This should only be called after having succesfully connected to Gmail.

        Return:
            The number of messages in the Gmail account that have at least one
            attachment (as advertised by Gmail).
        """
        limit = self.limit if self.limit > 0 else False
        gm_ids = self.inbox.search("has:attachment", gm_ids=True, limit=limit)
        return len(gm_ids)

    def extract(self, callback=None):
        """Extracts attachments from Gmail messages and writes them to the
        path set at instantiation.

        Keyword Args:
            callback -- An optional funciton that will be called with updates
                        about the image extraction process. If provided,
                        will be called with either the following arguments

                        ('image', attachment_name, disk_name)
                        when writing a message to disk, where
                        `attachment_name` is the name of the attachment
                        as advertised in the Email message, and `disk_name`
                        is the name of the file as written to disk.

                        ('message', first)
                        when fetching messages from Gmail, where `first` is the
                        index of the current message being downloaded.

        Returns:
            The number of attachments written to disk.
        """
        def _cb(*args):
            if callback:
                callback(*args)

        attachment_count = 0
        num_messages = 0
        offset = 0
        per_page = min(self.batch, self.limit) if self.limit else self.batch
        # Keep track of which attachments belong to which messages.  Do this
        # by keeping track of all attachments downloaded to the filesystem
        # (used as the dict key) and pairing it with two values, the gmail
        # message id and the hash of the attachment (so that we can uniquely
        # identify the attachment again)
        self.mapping = {}
        hit_limit = False
        while True and not hit_limit:
            _cb('message', offset + 1)
            messages = self.inbox.search("has:attachment", full=True,
                                         limit=per_page, offset=offset)
            if len(messages) == 0:
                break
            for msg in messages:
                for att in msg.attachments():
                    if att.type in ATTACHMENT_MIMES:
                        poss_fname = u"{0} - {1}".format(msg.subject, att.name())
                        safe_fname = sanatize_filename(poss_fname)
                        fname = unique_filename(self.dest, safe_fname)

                        _cb('image', att.name(), fname)
                        h = open(os.path.join(self.dest, fname), 'w')
                        h.write(att.body())
                        h.close()

                        self.mapping[fname] = msg.gmail_id, att.sha1(), msg.subject
                        attachment_count += 1
                num_messages += 1
                if self.limit > 0 and num_messages >= self.limit:
                    hit_limit = True
                    break
            offset += per_page
        return attachment_count



