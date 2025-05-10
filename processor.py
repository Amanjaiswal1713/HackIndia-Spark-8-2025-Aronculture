import whisper
import openai
from openai.error import RateLimitError, AuthenticationError, InvalidRequestError, OpenAIError
from moviepy import TextClip, concatenate_videoclips, CompositeVideoClip
import os
import smtplib
from email.message import EmailMessage
from slack_sdk import WebClient

openai.api_key = "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"

def transcribe_audio(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result['text']

def summarize_text(transcript):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You summarize meeting transcripts."},
                {"role": "user", "content": transcript}
            ]
        )
        return response['choices'][0]['message']['content']

    except RateLimitError:
        return "Error: You have exceeded your API quota. Check your OpenAI usage at https://platform.openai.com/account/usage."

    except AuthenticationError:
        return "Error: Invalid API key. Please check your key at https://platform.openai.com/account/api-keys."

    except InvalidRequestError as e:
        return f"Error: {str(e)}. This could be due to model access or incorrect parameters."

    except OpenAIError as e:
        return f"An OpenAI error occurred: {str(e)}"

    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

def create_recap_video(summary_text, output_path="recap_video.mp4"):
    try:
        lines = summary_text.strip().split("\n")
        clips = []

        for line in lines:
            if line.strip():
                clip = TextClip(
                    txt=line.strip(),
                    fontsize=40,
                    color='white',
                    size=(1280, 720),
                    bg_color='black',
                    font='Arial',
                    method='caption'
                ).set_duration(4)
                clips.append(clip)

        final_video = concatenate_videoclips(clips, method="compose")
        final_video.write_videofile(output_path, fps=24)

    except Exception as e:
        print(f"Error generating recap video: {e}")

def send_email_with_video(to_emails, video_path):
    msg = EmailMessage()
    msg['Subject'] = 'Meeting Recap Video'
    msg['From'] = 'your_email@gmail.com'
    msg['To'] = ', '.join(to_emails)
    msg.set_content('Hi Team,\n\nPlease find the attached meeting recap video.')

    with open(video_path, 'rb') as f:
        msg.add_attachment(f.read(), maintype='video', subtype='mp4', filename='recap_video.mp4')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login('your_email@gmail.com', 'your_app_password')
        smtp.send_message(msg)

def send_slack_video(token, channel_id, video_path, message="Here is the meeting recap video:"):
    client = WebClient(token=token)
    client.files_upload(
        channels=channel_id,
        file=video_path,
        title="Meeting Recap",
        initial_comment=message
    )

def process_meeting_audio(audio_path):
    transcript = transcribe_audio(audio_path)
    summary = summarize_text(transcript)
    create_recap_video(summary)

    video_path = "static/recap_video.mp4"
    send_email_with_video(["teammate@example.com"], video_path)
    slack_token = "xoxb-your-slack-bot-token"
    channel_id = "C123456789"
    send_slack_video(slack_token, channel_id, video_path)