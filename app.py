import sys, os
import argparse
from gmailextract.extractor import GmailExtractor

parser = argparse.ArgumentParser(description='Extract attachments from a gmail account.')
parser.add_argument('-e', '--email', type=str, default="",
                    help='The email of the account to search for attachments in.')
parser.add_argument('-p', '--password', type=str, default="",
                    help='The password of the account to search for messages in.')
parser.add_argument('-d', '--dest', type=str, default=".",
                    help="The path where attachments should be downloaded.")
parser.add_argument('-l', '--limit', type=int, default=0,
                    help="The total number of messages that should be downloaded from GMail. Default is 0, or all.")
parser.add_argument('-s', '--simultaneous', type=int, default=10,
                    help="The maximum number of messages that should be downloaded from GMail at a time (defaults to 10).")
args = parser.parse_args()

extractor = GmailExtractor(args.dest, args.email, args.password,
                                limit=args.limit, batch=args.simultaneous,
                                replace=args.write)

# Next, see if we can succesfully connect to and select a mailbox from
# Gmail. If not, error out quick
if not extractor.connect():
    print "Error: Unable to connect to Gmail with provided credentials"
    sys.exit()

# If we're able to connect to Gmail just fine, then we pull down a list of
# all the gmail messages that have attachments in the user's email account
num_messages = extractor.num_messages_with_attachments()
print "Found {0} messages with attachments".format(num_messages)

def _status(*status_args):
    if status_args[0] == 'message':
        print u"Fetching {0} messages starting with {1}".format(args.simultaneous, status_args[1])

attachment_count = extractor.extract(_status)
print "Succesfully stored {0} attachments to disk".format(attachment_count)

