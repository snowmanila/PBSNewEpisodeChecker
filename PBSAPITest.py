import requests
import os
import time

from datetime import datetime, timedelta

def main():
    start_date = datetime.now().date()
    episodes = []
    # Reads all dates between now and a year from now
    for i in range(0, 366):
        date = start_date + timedelta(days=i)
        url = f'https://schedule.whro.org/tv?date={date}&station=TVKIDS'

        # Send a GET request to fetch the webpage content (Returns None if page fails)
        schedule = requests.get(url)
        if (schedule.status_code) == 200:
            newDate = True
            response = schedule.text
            # Exits program when no schedule is posted (date limit reached)
            if response.__contains__('Selected date has no programs to display.'):
                break
            
            # Reads every episode detail on PBS WHRO's Kids schedule
            while response.__contains__("<p class='mb0'>"):
                response = response[response.find("<p class='mb0'>")+15:]
                response2 = response[:response.find("<div class='col-md-1 pl2 airtime time'>")]
                showtime = response2[:response2.find('</p>')] # Air time of show
                # Show name
                show = response2[response2.find("<a href='/program?programid=")+28:]
                show = show[show.find("'>")+2:show.find("</a>")+1]
                # Episode name
                episode = 'episode-0'
                if not response2.__contains__("<h3 class='episodeTitle my0'> "):
                    episode = response2[response2.find("<h3 class='episodeTitle my0'>")+29:response2.find('</h3>')]
                episode = episode.replace(' / ', '/')
                show = show[:show.find("</a>")]
                desc = 'No description available.'
                if response2.__contains__("<p class='episodeDesc mb0 mt1 font-light'>"):
                    desc = response2[response2.find("<p class='episodeDesc mb0 mt1 font-light'>")+42:response2.find("</p></div><div class='col-md-2'>")]
                # If new episode is detected, crosscheck with PBS WGTE for potential mislabeling
                # (some already aired episodes labeled as 'new' on WHRO)
                if episode not in episodes and response2.__contains__("<span class='new'>"):
                    crossShow = show.replace(' ', '-')
                    crossShow = crossShow.replace("'", '')
                    crossShow = crossShow.replace(' + ', '')
                    crossShow = crossShow.replace(' & ', '-and-')
                    crossShow = crossShow.replace(':-', '-')
                    crossEpisode = episode[:episode.find(' <span')].replace('episode-', 'episode-0')
                    crossEpisode = crossEpisode.replace(' ', '-')
                    crossEpisode = crossEpisode.replace('/', '-')
                    crossEpisode = crossEpisode.replace("'", '')
                    crossEpisode = crossEpisode.replace(',', '')
                    crossDate = date.strftime("%m/%d/%Y").replace('/', '-')
                    crossTime = showtime.replace(':', '-')
                    if crossTime[1] == '-':
                        crossTime = '0' + crossTime
                    crossResponse = requests.get(f'https://www.wgte.org/schedules/program/kids/{crossShow}/{crossEpisode}/{crossDate}/{crossTime}-00')
                    # If page exists on PBS WGTE
                    if crossResponse.text.__contains__('Previous Episodes'):
                        crossText = crossResponse.text[crossResponse.text.find('</td><td>')+9:]
                        crossText = crossText[crossText.find('</td><td>')+9:]
                        # If new episode hasn't aired (according to WGTE)
                        if crossText[:crossText.find('</td>')] == crossDate.replace('-', '/'):
                            # If first new episode entry on date
                            if newDate:
                                print(f'\nNew episodes for {date}:')
                                newDate = False
                            episodes.append(episode)
                            episodeNew = episode[:episode.find(' <span ')]
                            desc = crossResponse.text[crossResponse.text.find('</h2><p>')+8:crossResponse.text.find('</p><p class="channel">')]
                            if crossResponse.text.__contains__(')<p>'):
                                desc = crossResponse.text[crossResponse.text.find(')<p>')+4:crossResponse.text.find('</p><p class="channel">')]
                            desc = desc.replace('&#039;', "'")
                            desc = desc.replace('&quot;', "'")
                            print(f'{show}: {episodeNew} - {desc}')
                    else:
                        crossTime = str(int(crossTime[:crossDate.find(':')-2])+12) + '-' + crossTime[crossDate.find(':')-1:]
                        crossResponse = requests.get(f'https://www.wgte.org/schedules/program/kids/{crossShow}/{crossEpisode}/{crossDate}/{crossTime}-00')
                        # If page exists on PBS WGTE
                        if crossResponse.text.__contains__('Previous Episodes'):
                            crossText = crossResponse.text[crossResponse.text.find('</td><td>')+9:]
                            crossText = crossText[crossText.find('</td><td>')+9:]
                            # If new episode hasn't aired (according to WGTE)
                            if crossText[:crossText.find('</td>')] == crossDate.replace('-', '/'):
                                # If first new episode entry on date
                                if newDate:
                                    print(f'\nNew episodes for {date}:')
                                    newDate = False
                                episodes.append(episode)
                                episodeNew = episode[:episode.find(' <span ')]
                                desc = crossResponse.text[crossResponse.text.find('</h2><p>')+8:crossResponse.text.find('</p><p class="channel">')]
                                if crossResponse.text.__contains__(')<p>'):
                                    desc = crossResponse.text[crossResponse.text.find(')<p>')+4:crossResponse.text.find('</p><p class="channel">')]
                                desc = desc.replace('&#039;', "'")
                                desc = desc.replace('&quot;', "'")
                                print(f'{show}: {episodeNew} - {desc}')
                        # If new episode but page does not exist on WGTE
                        elif episodeNew not in episodes:
                            episodes.append(episode)
                            episodeNew = episode[:episode.find(' <span')]
                            if newDate:
                                print(f'\nNew episodes for {date}:')
                                newDate = False
                            print(f'{show}: {episodeNew} - {desc}')

os.system('cls') # Clears terminal; replace with os.system('clear') if on Unix/Linux/Mac
main()