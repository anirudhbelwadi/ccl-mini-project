# ==================================================================================
# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.

# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# ==================================================================================
#
# translatevideo.py
# by: Rob Dachowski
# For questions or feedback, please contact robdac@amazon.com
#
# Purpose: This code drives the process to create a transription job, translate it into another language,
#          create subtitles, use Amazon Polly to synthesize an alternate audio track, and finally put it all together
#          into a new video.
#
# Change Log:
#          6/29/2018: Initial version
#
# ==================================================================================


import argparse
from fileinput import filename
from transcribeUtils import *
from srtUtils import *
import time
from videoUtils import *
from audioUtils import *


def translate(file, fileUrl, fileType, language):

    # Get the command line arguments and parse them
    # parser = argparse.ArgumentParser(
    #     prog='translatevideo.py', description='Process a video found in the input file, process it, and write tit out to the output file')
    # parser.add_argument('-region', required=True,
    #                     help="The AWS region containing the S3 buckets")
    # parser.add_argument('-inbucket', required=True,
    #                     help='The S3 bucket containing the input file')
    # parser.add_argument('-infile', required=True,
    #                     help='The input file to process')
    # parser.add_argument('-outbucket', required=True,
    #                     help='The S3 bucket containing the input file')
    # parser.add_argument('-outfilename', required=True,
    #                     help='The file name without the extension')
    # parser.add_argument('-outfiletype', required=True,
    #                     help='The output file type.  E.g. mp4, mov')
    # parser.add_argument('-outlang', required=True, nargs='+',
    #                     help='The language codes for the desired output.  E.g. en = English, de = German')
    # args = parser.parse_args()

    region = "us-east-1"
    bucket = "mybucket-ccl-1234"
    fileName = file.split(".")[0]

    # print out parameters and key header information for the user
    # print("==> translatevideo.py:\n")
    # print("==> Parameters: ")
    # print("\tInput bucket/object: " + bucket + file)
    # print("\tOutput bucket/object: " + bucket +
    #       fileName + "." + fileType)

    # print("\n==> Target Language Translation Output: ")

    # for lang in args.outlang:
    #     print("\t" + args.outbucket + args.outfilename +
    #           "-" + lang + "." + args.outfiletype)

    # Create Transcription Job
    #print(args.region, args.inbucket, args.infile)
    response = createTranscribeJob(region, bucket, file)

    # loop until the job successfully completes
    # print("\n==> Transcription Job: " +
    #       response["TranscriptionJob"]["TranscriptionJobName"] + "\n\tIn Progress"),

    while(response["TranscriptionJob"]["TranscriptionJobStatus"] == "IN_PROGRESS"):
        # print("."),
        # time.sleep(30)
        response = getTranscriptionJobStatus(
            response["TranscriptionJob"]["TranscriptionJobName"])

    print("\nJob Complete")
    print("\tStart Time: " + str(response["TranscriptionJob"]["CreationTime"]))
    print("\tEnd Time: " + str(response["TranscriptionJob"]["CompletionTime"]))
    print("\tTranscript URI: " +
          str(response["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]))

    # Now get the transcript JSON from AWS Transcribe
    transcript = getTranscript(
        str(response["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]))
    # print( "\n==> Transcript: \n" + transcript)

    # Create the SRT File for the original transcript and write it out.
    writeTranscriptToSRT(transcript, 'en', "subtitles-en.srt")
    createVideo(file, "subtitles-en.srt", fileName +
                "-en." + fileType, "audio-en.mp3", True)

    # Now write out the translation to the transcript for each of the target languages
    for lang in language:
        writeTranslationToSRT(transcript, 'en', lang,
                              "subtitles-" + lang + ".srt", region)

        # Now that we have the subtitle files, let's create the audio track
        createAudioTrackFromTranslation(
            region, transcript, 'en', lang, "audio-" + lang + ".mp3")

        # Finally, create the composited video
        createVideo(file, "subtitles-" + lang + ".srt", fileName +
                    "-" + lang + "." + fileType, "audio-" + lang + ".mp3", False)


#translate('combined.mp4', 'mp4', ['en', 'de'])
