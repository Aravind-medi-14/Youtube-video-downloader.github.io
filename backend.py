from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp
import threading

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    url: str
    quality: str

ydl_opts = {
    'outtmpl': '%(title)s.%(ext)s',
    'ffmpeg_location': 'D:\\Projects\\yt vid down\\ffmpeg-master-latest-win64-gpl-shared\\bin',
}
quality_mapping = {
    "1080p": "136+140",
    "720p": "240+140",
    "480p": "360+140",
    "360p": "480+140",
}

def download_video(url, quality):
    ydl_opts['format'] = quality_mapping.get(quality, "best")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            print(f"Video '{info.get('title')}' downloaded successfully!")
    except yt_dlp.utils.DownloadError as e:
        print(f"Download error: {str(e)}")
        # If the requested format is not available, try downloading in the best available format
        ydl_opts['format'] = "best"
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                print(f"Video '{info.get('title')}' downloaded successfully in best available format!")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

@app.post("/download/")
async def download_video_endpoint(video_request: VideoRequest):
    url = video_request.url
    quality = video_request.quality
    threading.Thread(target=download_video, args=(url, quality)).start()
    return JSONResponse(
        content={"message": "Video download started!"},
        media_type="application/json",
    )
