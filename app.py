import streamlit as st
import time
from model import get_rag_chain

# --- 1. CONFIGURATION AND STYLING ---

st.set_page_config(
    page_title="C-LangBot: AI C Assistant",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- 1.1. CSS FOR FUTURISTIC UI & ANIMATIONS ---
st.markdown("""
<style>
/* 1. Base Theme */
.stApp {
    background-color: #0A0A10; 
    color: #DDE6ED; 
    font-family: 'Inter', sans-serif;
}

/* 2. Logo and Header Styling */
.header-container {
    text-align: center;
    padding: 3rem 0 1rem;
    max-width: 600px;
    margin: 0 auto;
}
.emoji-logo {
    font-size: 3.5rem; 
    display: block;
    margin-bottom: -15px; 
    color: #4CC9F0; 
    text-shadow: 0 0 15px #4CC9F0, 0 0 30px #4CC9F080;
}
.navbar-logo {
    position: fixed;
    top: 15px;
    left: 20px;
    z-index: 1000;
}
.logo-title {
    font-size: 2.5rem;
    font-weight: 700;
    color: #4CC9F0;
    text-shadow: 0 0 10px #4CC9F0, 0 0 20px #4CC9F080;
    margin-top: 10px;
}
.logo-subtitle {
    color: #8C9EFF;
    font-size: 1.1rem;
}

/* Book Cover Styling */
.book-container {
    display: flex;
    justify-content: center;
    margin: 20px 0 40px;
}
.book-cover {
    width: 120px;
    height: 160px;
    border-radius: 8px;
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.5), 0 0 10px #4CC9F0;
    object-fit: cover;
}


/* 3. Page Load Zoom Animation */
@keyframes zoomOut {
    0% { transform: scale(1.2); opacity: 0; }
    100% { transform: scale(1); opacity: 1; }
}
.zoom-container {
    animation: zoomOut 1.5s ease-out forwards;
    animation-delay: 0.5s;
    opacity: 0; 
}

/* 4. Chat Message Animations */
@keyframes fadeInSlide {
    0% { opacity: 0; transform: translateY(20px); }
    100% { transform: translateY(0); }
}
div.stChatMessage {
    animation: fadeInSlide 0.5s ease-out;
}

/* 5. Chat Bubble Styling */
.stChatMessage:not([data-testid="stChatMessage-0"]) .stMarkdown {
    background-color: #1A1A2E; 
    border: 1px solid #33334F;
    border-radius: 12px 12px 12px 0; 
    padding: 12px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.4);
}
.stChatMessage:not([data-testid="stChatMessage-0"]) .stMarkdown p {
    color: #DDE6ED !important;
}

[data-testid="stChatMessage"] .stMarkdown {
    background-color: #DDE6ED; 
    border: 1px solid #C5C9E0;
    border-radius: 12px 12px 0 12px;
    padding: 12px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}
[data-testid="stChatMessage"] .stMarkdown p {
    color: #1A1A2E !important; 
}
.stChatMessage .stMarkdown {
    color: initial; 
}

/* 6. Typing Indicator Animation */
@keyframes bounce {
    0%, 80%, 100% { transform: translateY(0); }
    40% { transform: translateY(-8px); }
}
.typing-dots span {
    display: inline-block;
    animation: bounce 1.4s infinite ease-in-out both;
    margin: 0 2px;
    color: #4CC9F0;
    font-size: 1.5rem;
    line-height: 0;
}
.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }

/* 7. Input Field Styling */
[data-testid="stTextInput"] input {
    background-color: #1A1A2E;
    color: #DDE6ED;
    border: 1px solid #33334F;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)


# --- 2. LOGO DEFINITIONS ---

TECHNO_LOGO = "〔・〕" 
BOOK_COVER_URL = "https://placehold.co/120x160/1A1A2E/4CC9F0?text=C+ANSI\nBook"

# Place the logo in the top-left corner (Navbar/Header)
st.markdown(f'<div class="navbar-logo"><span class="emoji-logo" style="font-size: 40px; margin: 0;">{TECHNO_LOGO}</span></div>', unsafe_allow_html=True)


# --- 3. INITIALIZATION AND PAGE LOAD ---

main_content_placeholder = st.empty()

with main_content_placeholder.container():
    st.markdown(
        f"""
        <div class="header-container">
            <span class="emoji-logo">{TECHNO_LOGO}</span> 
            <div class="logo-title">C-LangBot</div>
            <div class="logo-subtitle">Your AI C Programming Assistant, powered by the ANSI C textbook.</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown(
        f"""
        <div class="book-container">
            <img class="book-cover" src="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBxISEhUSEhIVFhUVFRUVFRUVFRcVFRUVFRYXFhcWFRcYHyggGBolGxUVITEhJSkrLi4uFx8zODMtNygtLisBCgoKDg0OGhAQGy0fHyUtLS0tLS0rKy0tLS0tLS0tLS0tLSstLS0tLS8tLS0rLS0tLS0tLS0tLS0tLS0tLS0tN//AABEIAQMAwgMBIgACEQEDEQH/xAAbAAABBQEBAAAAAAAAAAAAAAADAAECBAYFB//EAEkQAAEDAQQFCQUGAwUHBQAAAAEAAhEDBBIhMQUTQVFxBiJSYXKBkaGxMkLB0fAUFSMzU6IWYpJzgrLh8QckNEPCw9IlY3SDs//EABsBAAMBAQEBAQAAAAAAAAAAAAECAwAEBQYH/8QALxEAAgECBQIEBAcBAAAAAAAAAAECAxEEEiExURNBFCIyUhVTcZEFI2GhsdHwgf/aAAwDAQACEQMRAD8A8lpUwQDdGQ2dSmKLeiPAJ7OOa3gPRFAV0jilJ3Big3ojwCcUG9EeARAFIBGwjmwWob0R4BPqG9EeARYUgEbCZ3yB1Dei3wCfUN6LfAIwCSOUV1HyBFBnRb/SE/2ZnQb4BGhKEcoOo+QP2dnQb/SE/wBnZ0W/0hFhPC2VA6kuQP2dnRb/AEhL7Ozot/pCNdShbKjdWXIH7Ozot8Am+zs6LfAI8JoWyoPUlyB1DOi3+kJtQ3ot8AjwmhbKg9R8gNQ3ot8AkaDeiPAI8KJCGUKm+QGob0R4BMaDeiPAI5CYhCwym+SvqG9EeATalvRHgEeExCFh1NlUsG5MiOzTpLHTdk7P7LeyPRFAUbO3mN7I9AigKiRxzerGATgKQCeEyRJyGTgKQC0nJ/k9RrWataa1pNFlF7GGKRqkmplk4bUW7AV5OyM1CldWg5Q8nBZ20atKqK9GuHGm9rCwyww5rmEkgj4LiasiMDjlgceG/uWTTFlFp6goTgIj6ZBhwIO4gg+BT6l2HNOOWBx4b0QWYKE8IgpOOTScJyOQzPBI0nReumJi9Bid05LAswcJQisouOTSdogE4DOITCmYvQYOAMGJ3TlKxrMHCYhG1LsTdMASTBgA5EnYEm0TLb0tB2kHLaRvidiwUmAhMQunpixU6dVzKNQ1mNiKmrcyZAOLTiMTCovYQYIIIzBBBHcVrhaaAkJiEd9Bwza4YTi0iBvM7OtWtDWSnVrMp1quqY4m9UDC+6IJHNGJkwO9C4UnexzSFEhW32clxDAXC8Q0hp50TjGwxjGxV3NW0G1QMhRhEhMQlaGTKjs06k/M8Ukh2J6BbOOY3sj0CKFCzDmN7LfQIwaqRWhxVH5mMApAJwE6ZEbihbnklbRR0XbahpUqoFezi5WbeYZgSRIxGYWIAUg8xEmDmJMHiEJRuNCeV3N5yP09VtekrIHtpsp0m1W06VJlymwat0wNswPBPyX0tXtVS1PvtdbGUCLEC2mAwXyXspCALwERPzWDY4gyCQd4MHxCdrjIIOIMgjMHfKHTHVd9z0TSd40LGdKga/7YBL7oqmye/rbvuXoz6lotHDSRt9XXAfY7lY0sKeru3DqtSRzr0Z9UzsXjzaxLw6pL4LS684y4A4tLs8RI71qqfKayUQ59lstWnVcx9NhqVzUp0RUEO1TNhhLKD7FIVovVh9J6WrUdF6Pp0n3BWpWhtQw285usu3S4gkN5xJjHJamx6NqM1lnqvtVakLG8Xnikyxu/CBaKTQJJG+ZwJK8jxgCSQMAJkDhuRNa+AL7oAIaLxhoOcbhwTOnoIsQk9UbmwaWrWeyaJbSfc1lWo15AaS9v2houEkezDjIEZdSuaXt76j9MWVxGoo0HupUw1obTcwtILYAMySeK85c93SOGIxyJxw3JrzsTeMnPE48d/ei6QFiLK3+2PWLNpSqNJ2Syhw1FSxsNSndaW1DqKhl8iT7I27OsrL2zSdW1aNquruvupW6kKZho1bXNdzG3QIbshY7WukG8ZGRkyOBUb5iJMHGJwnfG9L0zPEHqNttLqNp0zUpwHss9nLSQDdN0QQDhIzHBC0fam136JtFrLXVHstTb7wAH1GOu0dZEA4+Z615oarseccc8Tjx3o+jrVTbUYazDVptJmmXFoII2EZY4oOnoMq93seiRpM2PSX3gD+QRTvCnIN7nau7jq8s+pY//AGeD/wBSsv8Aaf8AQ5WLfyis4oVaNkoVGa8NbVqVqutdq2mRTZuErLteRiCQd4MFaMXZhnUWZW1sbhmlq1l0U2pQfcebfWbfAaXXbpN0SMJIE7wuZ/tOYBb3kAC9TovdAgFzqYJPes0XmIkxnE4TvjeoveTiSSd5MlMo2dxJVbqwEhRKKQouCawkWVHjE8UkqgxPEpKOh3rYsWb2G9lvoEYIdlHMb2W+gRYVo7HBUfmYgpBh3JMRL6ZE2yNw7kmtlEvpAwmshbkQwpwxElPK1kLmBPbAW3+56FOGGixzmtaHOdekvDReJ5w9694LN6Ds4qWiiw5X77uzTBqO8mEd62dmh9QF5wLrzzub7Tj4Aoxim232EqTkklHdnNtOjKLqdQNosa/VucwtvA3mC/GLtoaR3rHPfgSNy9CnV1MfdfjwBj0XnmmaWqqVqXQe9o6wCbp7xB71p2Ww1G89Humbq2aKs7XuaLPTgGBN+f8AEuNylsDGURVpMDLr7rw2Yh45jsSci0j+8FpdI/mv4/AKrVs2tY+iTGtYaYO5xxY7ueGnuTOHkuiUar6tpPS4B2irOLv+70zzKZxvEkljSSedvKz/ACnsrWV6bKVMNv0qZuNnF7nPbhJzMBaozDJEHV0pG46tuC4ml6obpGxl3s3LPJ2Y1agHnB7lOaSimXpOUqkovt/ZZsegKNIAVGirUHtFxOradoa0EXoyl2ewK2bBRjGz0YP/ALTQO4gZormnEHMYHiqpZWbaala8+rQqMcDSYb1SkQAW3aTiA4NLcCzGDkqSSilpclCUqsnaVn2RztLcn6ZY6pQBa5jS51OS5rmDFxZOIIGMYyAYTcmdH0X0HvqUmvdrgwF17BurDoEEbVYocq7K13/OlsgtNJoOUFpl+G5R5Hf8I/8A+QP/AMgp+VyVtiz6kabctGF0hoyhqaxbQY1zaTnNLb0hwLYOLisYRvW+t35Ff+wf6tWEcUZpJ6C0puUE2CKaFJNCQqinUzPEpJVDieJTqB6C2D2UcxvZb6BGCFZvYb2W+gRmq0djgqepjgKQYnpmEQFOrEmyF1SDVKZUgmshGyIanOCcuSs9CpVdcptLjnhsG8nYFtDJNna5I05dWq9FjaY7VR0n9rHeK7lppPdSrCkJeaNRrACASXwzAkgYBxPcg6K0ebPQawmXPc6q6BH8jR1+wT3q9Ss94F15oAIHOnEkE4QDsCaMfI79yc5fmrLrYa0B0i/F4splwBBhxY28JHXKraQ0HQqTXc2XVKYmSYvUwKZwHUwHvVirRugGWkGQC2c2xIxA3jxT2i0NZZ3OcYFN4M/yvaRHi0eKZpZV3FhKWd9rhdKN/FqD+YjwUtJ0QCxwOD2MdwddbeHGSD3hR0mfxqnaPmgOtZdUfRPu0aFZm/BjW1B4XXf3Ss3bKZRzZw1vtOsff2lrJ7QaAfSe9WNW11wOaD+C3YD7z+pc9J+lTTtVnpQLrqTW3jILS81WA+JCE9EjUbycmdC00g84hzXdK44td2gBIPWPDaqdag5mY4EGQeB2pm1ng+07A5Xjs2K3VqN/EN5pa+8WtBM3nOvAkRAIE4yteUfoB5JpvZo5GkdDstfNMNrRDKsYyMmVOmDkCcQdsYJaE0a6hZ3NcQb1eQWz+kBtXR0YPxWHYHBx4N5x8gVJ4/B/+3/thBxSmh1UlKi7nOt/5Ff+xf6hYQtW8tv5Nf8AsX+rViHZIVF5h6L/AC0AIUURwUSFMsmUqjMTxKSI/M8Uy5z0VsGso5jey30CMAhWUcxnZb6BWKeC6I7I8+q/MxAIl1IKcp7Ig2MGpFSlWNG2B1oqCm3LNztjW7StYC1FonRL7S+G4NHtOOQ6hvK3Fi0YKNMspiJzMySeuMSVbsVkZSYGUxAHiTvPWjqsYWJTqN6LYqVqDXEYVMGtaMGnBrQM5xxk96mylDWhoODi43oBxDQMiRhdPipVQ6cMsP8AP4LnaX0k6i0dJ03Zjx7kcthXO/YDpHSNKl+G8OJvl8Muki9AIMkdFuHFc22aWovo1aYZVl7Lom5AdILXGDsIC5DsTJMknEnMylcU2v1KqSTTtqaC08oKLnF2rqicYhmGHFc+tpIfaWV2tdda2mwtdEuYGXHjDDFpd5LnlsJXfgtlNns20juffdHoVvBn/kuZpq1trPa5ocA2m1nOicC4zzTh7W/YqpHWmLVmuQZrbI69m0/IArscSP8AmMIl3W9hwJ6wRO1WqemLMSAX1BO+mBHE38As4WqLgtqtma8W9UeiUqIAhogHMky5wzjDAN6h4lRtxa2k4kON0mpzYMgNgjEjcuTyT0iXtNJx5zPZ62bu75Lt2tkseN7HDxaU9k0LmadjJWvTtJ1OoxrKsvYWC9cgSRiYPUs2WopUCp27ls2lkBIUCEZyGQkaHiyk/M8Uk78zxKS57HqLYPYxzGdlvoFYAQbF7DOy30CtArogtDzar8zGAUwEgnhPZEGyLjsW50Hox1CmBHOdBeRnO6er5rgck7DrK18jm0+dxcfZHqe5blPBdxKkrKxXDqm7fu3KTb+3uy8+tGVdr37thxg+XkqEBqgcJLjAjEjYAZO7YsZbrSary8nPBo3AZD63rQcobW5tG7tebuUYDE+kd6y4Zt+sUsmPFCDeCYMU7oSubz9QlGImD/qnDOtO1nWP9EgI2j6C1jENWld+vFSu4ZpFuEdSxiICgQiXcZ+u9MWIaBC6NtJpVWPGw48DgfJegD1+K82uK2dLV7tzWuuxEdWUTmimkBq5QtDIc4biR4GEEhFcolLZDpgiFAoqg5K0UTKFTM8SkmqjE8SnXMestixY/wAtnYb6BWAECx/ls7DfQKwFeGx5lX1Mk1O4pBJ4mBvwTke5s+TFlLbO0jOoXPOMQPZbPcJ711nl3Xme/Ex8FOy0QxjWgey1o8BHwSdVM7vo/JWirIhJ3Y3OB38e/b1YJnPdjHXhnv8AkPFJ1Y7cOsY5ZpXjsIwE8Ywj63Iima5S1S6qGn3G+ZJ+ELltZv8Aoyrek33q1Q9ceAA+CCFO5UDqfrgiObPUPmigJwELgAarPyTOo4nLb5o9NkBOWo3MViw+vw+STmfBHICiQg2EAGJyiEKJCDMDIQnBHKG4IBAOCiQiOCgUTIEQoEIhUClZRHPq5niUk9Uc48T6pLnPYjsWLH+WzsN9ArAQLF7DOy30CsBWhseXW9TJBGsbL1WmN72/4ghBWdGfn0u231TkVub4VHQCdvDOOrrSBcROGHVwyR3mAha7q6hjtVznE6sY8eGE5JhVM5Z4T4wnvk7jjn69e9RdaCD6eOM9wWMY6ufxH9t3qVB1PGeHw+Sesw6x/U93+IpaskyMMs+B+amirH1Jw6jPmpOpkmcRht4zsTal2/PrOGeHmiCgd84jM7isAGKTt+7CTv8A8lIUevZHUeKnTpkEmJnYMds/FQNA7D5nPH5hEwM0T1ZR1zEKbk+qdOJ9cc/mPBQfTOMRsz78fNBmGIUCpgKJShIFQKIVArBAvQ3Ir0JyxgZCgUQqBQHRzqvtHiUk9U848T6pLnuewtixYvy2dlvoFYCr2I/hs7LfQKyFaGx5lb1MmEWyPu1abtz2nzCCEn7CmILc9INfYRnO3j8k4r5Yefx8U9neHta8Rzmh3iJRYVyNiu55GIAykcCRHf8AJSpvkOOzGPDNGu/X1wTFg+sAsAxlqbFWoP5ifHH4ob2Ex9bQrXKOkRaCR7zQ74fBU7rthU7FWTbTMf07YxGaLdkNbjIImJGWcFBax4iPX6wU2MdBGOJBzjERPnKICYpvwnHfjgcsvNMKToxdjhOOBw8sZUs2tbjIInMZZwVAB+E9U4jGIy3bVjEQxwOOPOmeqMeCkVG66MceruGRQ2NI8p880LGJOQyiFDKUJAqDkqroVfXIXGSbCOQnKcqDkQMgUMohQ3IDROfV9o8T6pJ6vtHiUlz2PZjsGsX5bOw30CstVayfls7LfQKw0qsNjzK3qf1CNUiFFqmE5zmx5LW4OoBhzpkt7sx6wuvrtwPX1Z/EFYvk5axTrXXezU5p6j7p8cO9bfVjKM8O4z81WDuhJrW4PX4xG2PKZT1K0GI+sVI0xnt3pwzftwKYUz/KhkhlQDIlp4GD64d65TCtZb7MHsNOPaBAO45g+IHgsTTvAkZHI9ynJalFqi+CoVbxwGUfP/JBLTxwIz6wpMvCNwnDxz3rIBKKm/b1fUKwSq1IxM93iVFoeBn6Z/JZ6mDkqBKFLts+WOz4qZKDMRcUNymSgVnwgFIq2uoqNN+Ke1VZWm5EaKDg6s9oI9lkgEfzHHuCT1Ox1eiF2cZmSZxWq5V2Sm2m1zWgOvRIESIOY7gsq5Paxy3vqRKGVMoZQKRKFUc48T6plKqcTxKZc9z14vQNY/y2dlvoFYCr2P2GdlvoFYBVYbHnVfUwjVMIbSphOc7JELccntJa6nDjz2YO6xsd9bViAUeyWl1J4qMOI8CNoPUinZg3Vj0RzgMSoGs3eqdk0kytTvCf5m7WnBWBTbid0z3D68FZEmrEy9v1s2ehWZ5SWQNcKzMjg/qOx3fl3LRAtOc95nd55KFVrCIIJDhjO0DCI8UGrhjKxiqL3Hb6dX+aLDoOc4fBR0vo91ndIk09hPu4kXXdeHeq7bQTkfTrU72dirjfVFsOwAnHCfioi9v2Ddu+aGyod/1BThx6SIoZpwTEqsX5dQ+ai+0YINpGUWw1Soubaq6avaFTMuMAEkmABiSepScjpp0+Qtjsrq1RtNmbjHAbSeoBeqWOzNpMbTbk0QOveT1k4964nJfRAs7Lz8ar4mMbjTs+a7mvHX7v7slanCyuyNepmdkZ/lnVwpt7TvQfErLOK7fK2terx0Wgd5kn1XDKEtxEiBUCpOKgUrKxKNX2jxKSarmeJSXKevHYNY/y2dlvorAVWxnmM7LfRWArR2PPqrzMKFNqG0qQKomc7QQFEaUIFTBREZZstodTdeYY3jYRuI2ha7ROk2VhdENdGLXZnCDdO1YoFTaf9UU7GaT3PRHNAjqy7sfgm1bT5+p+JWVsen6jYD+eBkcnDAjPbmu7YdKUXYB8E+6RBVFJMm4tFurZg4FpxBwIOMjE4+Pksrpfku9suoG8OgTDhwJzWt1w+gpgrSimGE3HY8sqPcwlrgWnc4EHwKX2lenWmy06gioxrh/MJXKrclbKfcLey4x4GVJwZdVYPdGDdaTvQnPcVvW8krOOmf7wHwVyz6AszMRSBO9xLvVbJIPWgtjz+waIrVzDGkja44NHErb6F5N06AvE3qnS2Dsj4rthsYAQNwySTxgkSnWlLREW0wPls3KBojM7Bn1DafBKvamM9t7W8SAuFpnT9M03MpklzhExAAOcTngmbJpXM3b7RrKj39JxPds8lVlOSoEqNyyRFxUSncVAlKyiRSqHE8SklUGJ4lJc56q2J2U8xnZb6BWGlVrL7DOy30CMFWOxw1V5mHapx9FdTkY8C2USTH5mMhpnVPiHHAGYxKJyjpVS81Kmswaxs1q1OtUxvRjTzHNOzDvRza2F6flucoeqmAc4MDM7BxW2MPsdOmXhrX0LK0OqVWarWCoA5raY57HwcX7gcFCtomiwPpMcxmtNmDmuqGARaKrTiXOcAWgHPaMpQVUZ4bhmNCcLX/cNm1ga1oeXChepmsKerD3vZUeCXEki63mkmLyCdCUILsLovs/MxFRtrFO7BM/lSfNFVkTeFkjMXinvFaduibPUL3U2hrKdS0MeDWk3GUXGk7Egm9UGzgpt0LRL6UBoa6i6o5j6hvuLdWJN10ZucRdIENO7FusuAeHkZ6z26qz2XkdUyPNdGhyjrNwIY4Rug7thV+02Cx0g8XdZcbaKgOuIvaquGMZA3sdnmYw2oeldF2ZlOtUYZ1b3UQ2+TNRxD6bxjiBTLgetoWVYDwzXAqfKjpUvB3zCMOVFPbTePA/FZS8mlWuzmyo1p5UUug/9vzQn8qm7KR73AegWWvJXkMzNZHdrcqKvusY3jLj8FQtGma786hA3Nho8lzyU0oNhSHe+cTid5xKgSkSoOKUZIclQJSJUCULlEhEqBKclQJSspFFWocTxKSZ+Z4lJc1z1FsSs3sN7LfQIwKDZvYb2W+gRFaOxw1PUwoKm2NgHgiaLotfVYx7i1rjDnATAgnr3Z7M12a3Jt4e4A3QxrXPvmS1r6j6bT+GCHexs45TEp4inCVpM0aUpK6OKIUhwXX0joLVXCKgeC8U3xIIJq1aYcAQMCKZ2kyDshXHcmm617WvNxl9skgvc9rXugXW3WjmiZjcleNpJXubw89jlaO0nUoTqyGzBxYx0FuTm3gbrhsIxVYukycZxJOJMrsv5OGCW1G4STg6GNa+q03obLj+F7oznZBVTSOh6lBt55Z7V0hpJLTz4nCIOrdkTkqU8VRk7J6sSdGolrsUpSEIYKeV03ObULKO+2vNNtKeYwktaABicyYEuPWdmCqSnlHcF2SlIlKmwuIDQSSYAGJJ3BaCzckLQ4S5zGdRlx74wXPiMZRw6/MkkWo4WrW9EbmflJaX+DKv6tPwcmPIyr+rT8HLj+NYL3r9zo+F4r2P9jNKLitN/BdX9Wn4OTHkTW/Vp+DlvjWC+YhvheK9jMwSokrUfwTW/Wp+Dk38EVv1qfg5D4zgvmIb4ZifYzLFQJWr/AIHrfrU/Byb+Ba361Pwcl+MYP5iGX4bifYZElMtaeQdb9an4PS/gOt+vT8HfJB/jGD+Yh/h2I9hhqhxPEpLR1+SVUOcNYwwSJx2FJP4qk9U/5OpUKi7Gfs3sN7LfQIsoNm9hvZb6BFXbHY82ovMw1Cq5hDmuLXDEFpII4EIxtlQzL37ffdtmdv8AM7xO9VAU4WcYt3YqbRbqWt7jznuORxcTkSRnuk+KKdJVjM1qhkQfxHYgZA44jE+JVEFOtkhwhbsust9URFR4gkiHuEEySRBzJJ8Sk6uXCC5x4uJymDjxPiVUlSBTRjFO6QrbYdJBBTqmYnlDSkHKCdMLlNryGsLbjq5HOJLGncBEkcT6K3bbXahVcxgN01KZa4MkNY24HtyxvF4x2Q7cpciP+FHbf/iXflfnuPxeXHVHNZtbfSx9pgaKWGgo6aGfo6TqE0y4vDPw21Tq3YP1VYvHszg8U8RIS19obnUqFpcbzyxpcxgrFl5oa3O7Gw4EmMFoJSC5fHU+1Nf7/h19N8nAqWyrPNfUJBYKbTThtSmRzqjzdEEG/tEXRhihv0lUcxjg6oDqWuaBScdZX99jwW4e7hh7RM4LRpFbx0Pl/wAf0bpvkzle3WhwusDr7XFrxdiCbQGthxaR+UTjjAxKMbXW/wB1lxF9hNU3SOdeZgfw3QcXCObMHFd1Mh46Gn5aN0nyZzRtqtDxSBfUIeG6xxpBpZUNKoXNEtAIBa3YYOEmUqdqrjVCpUqBjqbHVKgpgua9wqG7AZhJDRlsA2rSJLePjf0L9jdJ8mcs1ttV5t9pLX1KTPYgt5oc4u3BwJ7JEbVok5SXNiK8arTjFR+g0IuP6mZth/Ef2nepSStn5j+071KZfTw9K+hyNO55RRqkNHAbupFFZ2/yCSS+hTZ4koxvsPrnb/IKbap+gEkkczFcY8CdVO/yCYV3b/IJJIZnyDJHgmazt/kE4ru3+QSSRzPkGSPBJlZ2/wAgmNd2/wAgkki5M2SPAxtDt/kFJld2/wAgkktmfJskeDbcl7fUbQDWugXnbBv6wuwNJ1el+1vyTpLwMRRpupJuK+yPZoSapxSfYb70q9P9rfkkdKVen+1vyTpKPh6XtX2RbPLkb70rdP8Aa35J/vSr0/2t+SSS3h6XtX2Qc8uRfedXpftb8kvvOr0v2t+SSS3h6XtX2Rs8uRfedXpftb8kvvOr0v2t+SSS3h6XtX2Rs8uRfedXp/tb8kx0nV6f7W/JOkt4el7V9kDPK25l7bpOrrH84e273W7z1J0kl6cYRstDmcnyf//Z" alt="C Book Cover">
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown('<div class="zoom-container">', unsafe_allow_html=True)

    # --- RAG Model Initialization ---
    if "qa_chain" not in st.session_state:
        st.session_state.qa_chain = None
        st.session_state.messages = []
        st.session_state.initial_load_complete = False

        with st.spinner("Initializing C-LangBot Model... This may take a moment."):
            try:
                st.session_state.qa_chain = get_rag_chain()
                st.session_state.initial_load_complete = True
            except Exception as e:
                st.error(
                    f"Failed to initialize the RAG Model. Check 'model.py' for errors, including file paths and model downloads. Error: {e}"
                )
                st.stop()

    # --- 5. CHAT INPUT AND RESPONSE GENERATION ---
    
    # 1. Capture prompt first
    if prompt := st.chat_input("Ask a C programming question..."):
        # 2. Append user message only when new input is submitted
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # 3. Rerun the script immediately to clear the chat input box and update history
        st.rerun()

    # --- 4. CHAT HISTORY AND DISPLAY ---
    if st.session_state.initial_load_complete:
        # Display all past messages from history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # --- PROCESS NEWEST MESSAGE ---
        # Only process the RAG chain if the last message was from the user (i.e., new prompt submitted)
        if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
            
            latest_prompt = st.session_state.messages[-1]["content"]

            # Display the assistant thinking message inside a dedicated chat bubble
            with st.chat_message("assistant"):
                # Use st.empty() to create a placeholder that we will update/clear later
                response_placeholder = st.empty()
                response_placeholder.markdown(
                    """
                    <div style='display: flex; align-items: center; color: #8C9EFF;'>
                        Finding the perfect answer for you...
                        <div class='typing-dots'>
                            <span>.</span><span>.</span><span>.</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Use the RAG Chain to get the response
                if st.session_state.qa_chain:
                    try:
                        # Fetch the complete response from the LLM
                        full_response = st.session_state.qa_chain.run(latest_prompt)
                        
                        # 1. Clear the thinking indicator content from the placeholder
                        response_placeholder.empty()

                        # 2. Rerender the final response using the same placeholder 
                        response_placeholder.markdown(full_response)
                            
                        # Append the assistant's final response to history
                        st.session_state.messages.append({"role": "assistant", "content": full_response})

                    except Exception as e:
                        error_message = f"An error occurred during query processing: {e}"
                        response_placeholder.empty()
                        st.error(error_message)
                        st.session_state.messages.append({"role": "assistant", "content": error_message})

    st.markdown('</div>', unsafe_allow_html=True)
