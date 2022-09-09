import os
import requests
import json
from bs4 import BeautifulSoup
import sys
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import pygame.locals
from pygame.locals import *

AL_API_KEY = 'ENTER API KEY HERE'
app_version = 'BETA'

def write_config(relative_path, config):
  # initialize config file if it does not exist
  with open(resource_path(relative_path), 'w') as f:
    json.dump(config, f)

def read_config(relative_path):
  # open an existing config file
  with open(resource_path(relative_path), 'r') as f:
    config = json.load(f)
  return config

def edit_config(config, relative_path, key, value):
  # edit the data and write it back to the file
  config[key] = value
  with open(resource_path(relative_path), 'w') as f:
    json.dump(config, f)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class button():
  def __init__(self, color, x,y,width,height, text=''):
    self.color = color
    self.x = x
    self.y = y
    self.width = width
    self.height = height
    self.text = text

  def draw(self,win,outline=None):
    #Call this method to draw the button on the screen
    if outline:
      pygame.draw.rect(win, outline, (self.x-2,self.y-2,self.width+4,self.height+4),0,3)
        
    pygame.draw.rect(win, self.color, (self.x,self.y,self.width,self.height),0,3)
    
    if self.text != '':
      font = pygame.font.SysFont('arial', 24)
      text = font.render(self.text, 1, (0,0,0))
      win.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))

  def isOver(self, pos):
    #Pos is the mouse position or a tuple of (x,y) coordinates
    if pos[0] > self.x and pos[0] < self.x + self.width:
        if pos[1] > self.y and pos[1] < self.y + self.height:
            return True 
    return False

class InputBox:
  def __init__(self, x, y, w, h, text=''):
    self.COLOR_INACTIVE = pygame.Color('lightskyblue3')
    self.COLOR_ACTIVE = pygame.Color('dodgerblue2')
    self.FONTsize_init = 32
    self.FONTsize = 32
    self.FONT = pygame.font.Font(resource_path('fonts/Apex-Regular.ttf'), self.FONTsize)
    self.rect = pygame.Rect(x, y, w, h)
    self.color = self.COLOR_INACTIVE
    self.text = text
    self.final_text = None
    self.txt_surface = self.FONT.render(text, True, self.color)
    self.active = False

  def handle_event(self, event):
    if event.type == pygame.MOUSEBUTTONDOWN:
      # If the user clicked on the input_box rect.
      if self.rect.collidepoint(event.pos):
        # Toggle the active variable.
        self.active = not self.active
      else:
        self.active = False
      # Change the current color of the input box.
      self.color = self.COLOR_ACTIVE if self.active else self.COLOR_INACTIVE
    mods = pygame.key.get_mods()
    if event.type == pygame.KEYDOWN and event.key != K_ESCAPE:
      if self.active:
        if event.key == pygame.K_RETURN:
          #print(self.text)
          self.final_text = self.text
          self.text = ''
        elif event.key == pygame.K_BACKSPACE:
          self.text = self.text[:-1]
        elif event.key == pygame.K_v:
          if mods and pygame.KMOD_CTRL:
            clipboard = str(get_clipboard())
            self.text += clipboard
            self.update()
          elif event.unicode != '':
            self.text += event.unicode
        elif event.unicode != '':
          #print(self.text)
          self.text += event.unicode
        # Re-render the text.
        self.txt_surface = self.FONT.render(self.text, True, self.color)

  def update(self):
    # Resize the box if the text is too long.
    self.final_text = None
    text_width, text_height = self.FONT.size(self.text)
    pad = 35
    while text_width > self.rect.w - pad:
      self.FONTsize = self.FONTsize - 1
      self.FONT = pygame.font.Font(resource_path('fonts/Apex-Regular.ttf'), self.FONTsize)
      text_width, text_height = self.FONT.size(self.text)
    while text_width < self.rect.w - pad and self.FONTsize < self.FONTsize_init:
      self.FONTsize = self.FONTsize + 1
      self.FONT = pygame.font.Font(resource_path('fonts/Apex-Regular.ttf'), self.FONTsize)
      text_width, text_height = self.FONT.size(self.text)
    width = max(self.rect.w, 0) #, self.txt_surface.get_width()+10)
    self.rect.w = width
    self.rect.h = text_height+10

  def draw(self, screen):
    # Blit the text.
    screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
    # Blit the rect.
    pygame.draw.rect(screen, self.color, self.rect, 2)

def get_second_RP(leaderboard):
  return leaderboard[1].split(', ')[2]

def user_is_leader(leaderboard, user):
  leader = leaderboard[0].split(', ')[1]
  if user == leader:
    return True
  else:
    return False

def get_user_RP(leaderboard, user):
  RP = None
  for i in leaderboard:
    if user == i.split(', ')[1]:
      RP = i.split(', ')[2]
      return RP
  return RP

def get_leader_RP(leaderboard):
  return leaderboard[0].split(', ')[2]

def make_leaderboard_from_list(list):
  A = []
  B = []
  C = []
  leaderboard = []
  for i in range(0, len(list)-1):
    if i%3==0:
      A.append(list[i])
    if i%3==1:
      B.append(list[i])
    if i%3==2:
      C.append(list[i])
  for k in range(0, len(A)-1):
    leaderboard.append(A[k]+', '+B[k]+', '+C[k])
  return leaderboard

def get_leaderboard():
  response = requests.get("https://apexlegendsstatus.com/live-ranked-leaderboards/Battle_Royale/PC")
  soup = BeautifulSoup(response.text, 'html.parser')
  #childs = []
  #for child in soup.descendants:
    #if child.name:
      #print(child.name)
      #childs.append(child.name)    
  #save_x(childs, 'descendants.txt')
  blog_titles = soup.findAll('span')
  spans = []
  for title in blog_titles:
    if title.text != '' and title.text != 'loading...':
      text = title.text
      if '\u00a0' in text:
        text = text.replace('\u00a0','',1)
      spans.append(text)
  #save_x(spans, 'spans.txt')
  list = []
  k = 0
  for i in spans:
    if i == '1':
      k = 1
    if k == 1:
      list.append(i)  
  #save_x(list, 'list.txt')
  leaderboard = make_leaderboard_from_list(list)
  #save_x(leaderboard, 'leaderboard.txt')
  return leaderboard

def save_x(x, path, check_for_existing=True):
  if check_for_existing:
    if not os.path.exists(path):
      with open(path, 'w') as outfile:
        json.dump(x, outfile)
  if not check_for_existing:
    with open(path, 'w') as outfile:
      json.dump(x, outfile)

def get_difference(uid, leaderboard):
  if uid != None:
    leader_RP = int(get_leader_RP(leaderboard).replace(',','',1))
    #user_RP = int(get_user_RP(leaderboard, user).replace(',','',1))
    user_info = get_player_name_and_rank(uid)
    if user_info != None:
      user_RP = user_info[3]
      user = user_info[0]
      if not user_is_leader(leaderboard, user):
        difference = user_RP - leader_RP
        difference = str(difference)
        #print(difference)
      elif user_is_leader(leaderboard, user):
        second = int(get_second_RP(leaderboard).replace(',','',1))
        difference = user_RP - second
        difference = '+'+str(difference)
        #print(difference)
      return difference

def get_difference_bottom(leaderboard, uid):
  k = 0
  if uid != None:
    user_info = get_player_name_and_rank(uid)
    if user_info != None:
      user = user_info[0]
      for i in leaderboard:
        k = k+1
        #print(i)
        if i.split(', ')[1] == user:
          #print('leaderboard index = '+str(k))
          break
      ladderpos = k
      if len(leaderboard) >= ladderpos+1:
        top_RP = int(leaderboard[ladderpos].split(', ')[2].replace(',','',1))
        top_user = leaderboard[ladderpos].split(', ')[1]
        top_user_pos = leaderboard[ladderpos].split(', ')[0]
        #leader_RP = int(get_leader_RP(leaderboard).replace(',','',1))
        #user_RP = int(get_user_RP(leaderboard, user).replace(',','',1))
        user_RP = user_info[3]
        user = user_info[0]
        difference = user_RP-top_RP
        difference = str(difference)
        #print(difference)
        if user_RP<top_RP:
          difference = ''
          top_user = ''
          top_user_pos = ''
        return difference, top_user, top_user_pos

def get_difference_top(leaderboard, uid):
  k = 0
  if uid != None:
    user_info = get_player_name_and_rank(uid)
    if user_info != None:
      user = user_info[0]
      for i in leaderboard:
        k = k+1
        #print(i)
        if i.split(', ')[1] == user:
          #print('leaderboard index = '+str(k))
          break
      ladderpos = k
      if len(leaderboard) >= ladderpos+1:
        bottom_RP = int(leaderboard[ladderpos-2].split(', ')[2].replace(',','',1))
        bottom_user = leaderboard[ladderpos-2].split(', ')[1]
        bottom_user_pos = leaderboard[ladderpos-2].split(', ')[0]
        #leader_RP = int(get_leader_RP(leaderboard).replace(',','',1))
        #user_RP = int(get_user_RP(leaderboard, user).replace(',','',1))
        user_RP = user_info[3]
        if not user_is_leader(leaderboard, user):
          difference = bottom_RP-user_RP
          difference = str(difference)
          #print(difference)
        if user_is_leader(leaderboard, user) or bottom_RP<user_RP:
          difference = ''
          bottom_user = ''
          bottom_user_pos = ''
        return difference, bottom_user, bottom_user_pos

def get_daily_difference(uid, player_starting_RP):
  if uid != None:
    #leaderboard = get_leaderboard()
    #leader_RP = int(get_leader_RP(leaderboard).replace(',','',1))
    #user_RP = int(get_user_RP(leaderboard, user).replace(',','',1))
    user_info = get_player_name_and_rank(uid)
    if user_info != None:
      user_RP = user_info[3]
      diff = user_RP - player_starting_RP
      #user = user_info[0]
      if diff <= 0:
        difference = str(diff)
        #print(difference)
      elif diff > 0:
        difference = str(diff)
        difference = '+'+str(difference)
        #print(difference)
      return difference

def get_user_ID(PLAYER_NAME):
  response = requests.get(f'https://api.mozambiquehe.re/nametouid?auth={AL_API_KEY}&player={PLAYER_NAME}&platform=PC')
  #print(response.status_code)
  if response.status_code == 200:
    x = response.json()
    if 'Error' not in x:
      #print(x['uid'])
      return x['uid']
    else:
      #print('User not found.')
      return None
  else:
    return None
  
def get_player_name_and_rank(PLAYER_UID):
  response = requests.get(f'https://api.mozambiquehe.re/bridge?auth={AL_API_KEY}&uid={PLAYER_UID}&platform=PC')
  #print(response.status_code)
  if response.status_code == 200:
    x = response.json()
    #print(x)
    if len(x) > 1:
      name = x['global']['name']
      rank = x['global']['rank']['rankName']
      div = x['global']['rank']['rankDiv']
      RP = x['global']['rank']['rankScore']
      ladder_pos = x['global']['rank']['ladderPosPlatform']
      return name, rank, div, RP, ladder_pos
  return None

def get_logo_for_rank(rank, div=''):
  loadstring = 'images/'+str(rank.lower())+str(div)+'.png'
  loadstring = loadstring.replace(' ','',1)
  if os.path.exists(resource_path(loadstring)):
    logo = pygame.image.load(resource_path(loadstring))
    return logo

def get_clipboard():
  ttext = pygame.scrap.get(pygame.SCRAP_TEXT)
  if ttext:
    ttext = str(ttext).replace("b'", "", 1)
    ttext = ttext.replace("\\x00'","",1)
    #print(ttext)
    return str(ttext).strip()
  else:
    return None
  
def main():
  # initilize the pygame module
  pygame.init()

  uid = ''
  seconds = 30
  fps = 30
  deadtime = 60

  fpsClock = pygame.time.Clock()
  fetch_counter = 0
  fetch_freq = fps*seconds
  
  dt_freq = deadtime*fps

  config_path = 'config/config.json'
  default_config = {"uid": "", "refresh_time": "30", "fps": "30", "automode": "True", "animated": "True", "deadtimeon": "False", "deadtimeduration": "60"}
  
  predlogo = pygame.image.load(resource_path('images/apexpredator1.png'))
  apexlogo = pygame.image.load(resource_path('images/apexlogo.png'))
  twitchlogo = pygame.image.load(resource_path('images/twitchlogo.png'))
  #dg_background = pygame.image.load(resource_path('images/dg_background.png'))
  bg_image = predlogo
  width, height = bg_image.get_width(), bg_image.get_height()
  screen = pygame.display.set_mode((width, height))
  pygame.display.set_caption('Apex Legends RP Tracker')
  pygame.display.set_icon(predlogo)

  pygame.scrap.init()

  # --- fonts
  font = pygame.font.Font(resource_path('fonts/Apex-Regular.ttf'), 36)
  smallfont = pygame.font.Font(resource_path('fonts/Apex-Regular.ttf'), 24)
  bigfont = pygame.font.Font(resource_path('fonts/Apex-Regular.ttf'), 100)
  inst_font = pygame.font.Font(None, 20)
  dev_font = pygame.font.Font(None, 16)
  outline_thickness = 2

  # --- texts to be rendered
  text = font.render('relyT', True, 'green', 'blue')
  textRect = text.get_rect()
  textRect.center = (width // 2, 219*height // 256)

  dev_text = dev_font.render('Daily RP Tracker (Stream Overlay) - developed by relyT', True, 'white', None)
  dev_textRect = dev_text.get_rect()
  dev_textPad = 5
  dev_textRect.center = (width // 2, height-2*dev_textRect.h-dev_textPad)

  dev_text2 = dev_font.render('Data retreived from apexlegendsstatus.com', True, 'white', None)
  dev_text2Rect = dev_text2.get_rect()
  dev_text2Rect.center = (width // 2, height-dev_textRect.h)

  version_text = dev_font.render(app_version, True, 'white', None)
  version_textRect = version_text.get_rect()
  version_textRect.center = (width - version_textRect.w, height-version_textRect.h)

  inst_text = inst_font.render('Search for Origin username:', True, 'white', 'black')
  inst_textRect = inst_text.get_rect()
  inst_textRect.center = (width // 2, 2*height//32)

  inst2_text = inst_font.render('Enter Origin user ID:', True, 'white', 'black')
  inst2_textRect = inst2_text.get_rect()
  inst2_textRect.center = (width // 2, 2*height//32)

  # --- input box specs
  in_box_width = width//2
  in_box_height = 32
  in_box_x = (width//2)-(in_box_width//2)
  in_box_y = 30

  # --- input boxes
  input_box1 = InputBox(in_box_x, in_box_y, in_box_width, in_box_height)
  input_boxes = [input_box1]

  # --- button specs
  button_box_width = 150
  button_box_height = 32
  button_spacing = 10
  button_box_x = (width//2)-(button_box_width//2)

  # --- buttons
  start_button_box_y = 100
  start_button = button('red', button_box_x, start_button_box_y, button_box_width, button_box_height, 'Start')

  get_user_button_box_y = start_button_box_y + button_box_height + button_spacing
  get_user_button = button('red', button_box_x, get_user_button_box_y, button_box_width, button_box_height, 'Find ID')

  enter_user_button_box_y = start_button_box_y + 2*(button_box_height + button_spacing)
  enter_user_button = button('red', button_box_x, enter_user_button_box_y, button_box_width, button_box_height, 'Enter ID')

  confirm_user_button_box_y = 14*height//16
  confirm_user_button = button('green', button_box_x, confirm_user_button_box_y, button_box_width, button_box_height, 'Confirm')

  # --- set up static variables
  max_character_length = 20
  monitor_top_preds = 100

  maxtextRect = bigfont.render('888888 RP', True, 'black', None).get_rect()
  frame_pad = 10

  # --- set up menu bools
  enter_user_menu = False
  get_user_ID_menu = False
  pred_race = False
  pred_race_2 = False
  dead_time = False
  daily_growth = False
  daily_growth_2 = False
  main_menu = True
  auto_mode = True
  animated = True
  dead_time_on = False

  # --- autostarts if config file is available
  if not os.path.exists(resource_path(config_path)):
    write_config(config_path, default_config)
    config = read_config(config_path)
  elif os.path.exists(resource_path(config_path)):
    config = read_config(config_path)
    seconds = int(config['refresh_time'])
    if seconds < 15:
      seconds = 15
      edit_config(config, config_path, 'refresh_time', seconds)
    fps = int(config['fps'])
    if fps < 15:
      fps = 15
      edit_config(config, config_path, 'fps', fps)
    if fps > 60:
      fps = 60
      edit_config(config, config_path, 'fps', fps)
    fetch_freq = fps*seconds
    uid = config['uid']
    if uid != "":
      player_info = get_player_name_and_rank(str(uid))
      if player_info != None:
        player_name = player_info[0]
        player_rank = player_info[1]
        player_div = player_info[2]
        player_RP = player_info[3]
        player_ladderpos = player_info[4]
        player_starting_RP = player_RP
        daily_growth = True
        pred_race = False
        pred_race_2 = False
        main_menu = False
        get_user_ID_menu = False
        enter_user_menu = False
    auto_mode = bool(config['automode']=='True')
    animated = bool(config['animated']=='True')
    dead_time_on = bool(config['deadtimeon']=='True')
    deadtime = int(config['deadtimeduration'])
    dt_freq = deadtime*fps
    
  # Game loop.
  while True:
    screen.fill('green')
    #screen.convert_alpha()
    
    for event in pygame.event.get():
      if event.type == QUIT:
        pygame.quit()
        sys.exit()
      # Handle events.
      if event.type == KEYDOWN:
        if event.key == K_ESCAPE:
          if not main_menu:
            main_menu = True
            pred_race = False
            get_user_ID_menu = False
            enter_user_menu = False
            daily_growth = False
            daily_growth_2 = False
            uid = ''
            input_box1.text = ''
          elif main_menu:
            if config["uid"] != "":
              player_info = get_player_name_and_rank(str(config["uid"]))
              if player_info != None:
                uid = config["uid"]
                daily_growth = True
                daily_growth_2 = False
                pred_race = False
                main_menu = False
                get_user_ID_menu = False
                enter_user_menu = False
                fetch_counter = 0
      if event.type == pygame.MOUSEBUTTONDOWN:
        if pred_race:
          #print('switching modes 1')
          daily_growth = True
          daily_growth_2 = False
          pred_race = False
          main_menu = False
          get_user_ID_menu = False
          enter_user_menu = False
          fetch_counter = 0
        elif daily_growth:
          #print('switching modes 2')
          daily_growth_2 = False
          pred_race = True
          main_menu = False
          get_user_ID_menu = False
          enter_user_menu = False
          daily_growth = False
          fetch_counter = 0
        elif daily_growth_2:
          pred_race = True
          daily_growth = False
          main_menu = False
          get_user_ID_menu = False
          enter_user_menu = False
          daily_growth_2 = False
          fetch_counter = 0
        if start_button.isOver(pygame.mouse.get_pos()) and main_menu:
          pred_race = True
          main_menu = False
          get_user_ID_menu = False
          enter_user_menu = False
          daily_growth = False
          daily_growth_2 = False
        if get_user_button.isOver(pygame.mouse.get_pos()) and main_menu:
          get_user_ID_menu = True
          pred_race = False
          main_menu = False
          enter_user_menu = False
          daily_growth = False
          daily_growth_2 = False
        if enter_user_button.isOver(pygame.mouse.get_pos()) and main_menu:
          enter_user_menu = True
          get_user_ID_menu = False
          pred_race = False
          main_menu = False
          daily_growth = False
          daily_growth_2 = False
        if confirm_user_button.isOver(pygame.mouse.get_pos()) and get_user_ID_menu and uid != None and uid != '' \
          or confirm_user_button.isOver(pygame.mouse.get_pos()) and enter_user_menu and uid != None and uid != '':
          daily_growth = True
          daily_growth_2 = False
          pred_race = False
          get_user_ID_menu = False
          main_menu = False
          enter_user_menu = False
          fetch_counter = 0
          edit_config(config, config_path, 'uid', uid)
      for box in input_boxes:
        box.handle_event(event)
    
    # --- pred race application logic ---
    # Update.
    if pred_race:
      if fetch_counter == 0:
        player_RP = get_player_name_and_rank(uid)[3]
        if player_rank == 'Apex Predator':
          if player_ladderpos <= monitor_top_preds:
            leaderboard = get_leaderboard()
            difftop = get_difference_top(leaderboard, uid)
            if difftop != None:
              if len(difftop[1]) > max_character_length:
                chop = len(difftop[1]) - max_character_length
                nametop = difftop[1][:-chop]+'...'
              else:
                nametop = difftop[1]
              top_string = '#'+str(difftop[2])+' '+nametop+' (+'+difftop[0]+')'
              difftexttop = smallfont.render(top_string, True, 'white', None)
              difftexttopRect = difftexttop.get_rect()
            diffbottom = get_difference_bottom(leaderboard, uid)
            if diffbottom != None:
              if len(diffbottom[1]) > max_character_length:
                chop = len(diffbottom[1]) - max_character_length
                namebottom = diffbottom[1][:-chop]+'...'
              else:
                namebottom = diffbottom[1]
              bottom_string = '#'+str(diffbottom[2])+' '+namebottom+' (-'+diffbottom[0]+')'
              difftextbottom = smallfont.render(bottom_string, True, 'white', None)
              difftextbottomRect = difftextbottom.get_rect()
      # Draw.
      if fetch_counter == 0:
        text = bigfont.render(str(player_RP)+' RP', True, 'white', None)
        textRect = text.get_rect()
        textRect.center = ((width // 2), height//2)
        frame_width = maxtextRect.w+frame_pad
        frame_height = textRect.h+frame_pad
        frame_x = (width // 2)-(frame_width//2)
        frame_y = (height // 2)-(frame_height//2)  
      text = bigfont.render(str(player_RP)+' RP', True, 'black', None)
      #screen.blit(predlogo,(0,0))
      screen.blit(text, (textRect.x+outline_thickness,textRect.y+outline_thickness))
      screen.blit(text, (textRect.x-outline_thickness,textRect.y+outline_thickness))
      screen.blit(text, (textRect.x+outline_thickness,textRect.y-outline_thickness))
      screen.blit(text, (textRect.x-outline_thickness,textRect.y-outline_thickness))
      text = bigfont.render(str(player_RP)+' RP', True, 'white', None)
      if player_rank == 'Apex Predator':
        if player_ladderpos <= monitor_top_preds:
          if player_ladderpos != monitor_top_preds: 
            screen.blit(difftextbottom,(width//2-difftextbottomRect.w//2,height//2+frame_height//2+frame_pad))
          if player_ladderpos != 1:
            screen.blit(difftexttop,(width//2-difftexttopRect.w//2,height//2-frame_height//2-difftexttopRect.h-frame_pad))
      screen.blit(text, textRect)
      if animated:
        if (fetch_counter+1) <= fps/2:
          pygame.draw.rect(screen, 'green', pygame.Rect((fetch_counter+1)*width/fps*2, 0, width, height))
        if (fetch_counter+1) >= fetch_freq-fps/2:
          pygame.draw.rect(screen, 'green', pygame.Rect((fetch_freq-(fetch_counter+1))*width/fps*2, 0, width, height))
      pygame.draw.rect(screen, 'white', pygame.Rect(frame_x,frame_y,frame_width,frame_height),  4, 10)  
      fetch_counter = (fetch_counter+1)%fetch_freq
      if fetch_counter == 0:
        if auto_mode:
          #print('auto switching')
          pred_race = False
          daily_growth = True

    if pred_race_2:
      if fetch_counter == 0:
        leaderboard = get_leaderboard()
        diff = get_difference(uid, leaderboard)
        text = font.render(diff, True, 'red', 'black')
        textRect = text.get_rect()
        plus_minus = font.render(diff[0], True, 'red', 'black')
        plus_minusRect = plus_minus.get_rect()
        textRect.center = ((width // 2)-(plus_minusRect.width//2), 219*height//256)  
      fetch_counter = (fetch_counter+1)%fetch_freq
      # Draw.
      screen.blit(predlogo,(0,0))
      screen.blit(text, textRect)

    # --- daily growth application logic ---
    # Update.
    if daily_growth_2:
      if fetch_counter == 0:
        diff = get_daily_difference(uid, player_starting_RP)
        text = font.render(diff, True, 'black', None)
        textRect = text.get_rect()
        if diff != '0':
          plus_minus = font.render(diff[0], True, 'red', 'black')
          plus_minusRect = plus_minus.get_rect()
          textRect.center = ((width // 2)-(plus_minusRect.width//2), 21*height//32)
        else:
          textRect.center = ((width // 2), 21*height//32)
      fetch_counter = (fetch_counter+1)%fetch_freq
      # Draw.
      logo = get_logo_for_rank(player_rank)
      if logo != None:
        screen.blit(logo,(0,0))
      text = font.render(diff, True, 'black', None)
      screen.blit(text, (textRect.x+outline_thickness,textRect.y+outline_thickness))
      screen.blit(text, (textRect.x-outline_thickness,textRect.y+outline_thickness))
      screen.blit(text, (textRect.x+outline_thickness,textRect.y-outline_thickness))
      screen.blit(text, (textRect.x-outline_thickness,textRect.y-outline_thickness))
      text = font.render(diff, True, 'white', None)
      screen.blit(text, textRect)

    # --- daily growth application logic ---
    # Update.
    if daily_growth:
      if fetch_counter == 0:
        diff = get_daily_difference(uid, player_starting_RP)+' RP'
        if diff == '0 RP':
          diff = '\u00B1'+diff
        text = bigfont.render(diff, True, 'black', None)
        textRect = text.get_rect()
        plus_minus = bigfont.render(diff[0], True, 'red', 'black')
        plus_minusRect = plus_minus.get_rect()
        textRect.center = ((width // 2)-(plus_minusRect.width//2), height//2)
      # Draw.
      #logo = get_logo_for_rank(player_rank)
      #if logo != None:
        #screen.blit(logo,(0,0))
      #frame_pad = 10
      if fetch_counter == 0:
        frame_width = maxtextRect.w+frame_pad
        frame_height = textRect.h+frame_pad
        frame_x = (width // 2)-(frame_width//2)
        frame_y = (height // 2)-(frame_height//2)
      text = bigfont.render(diff, True, 'black', None)
      screen.blit(text, (textRect.x+outline_thickness,textRect.y+outline_thickness))
      screen.blit(text, (textRect.x-outline_thickness,textRect.y+outline_thickness))
      screen.blit(text, (textRect.x+outline_thickness,textRect.y-outline_thickness))
      screen.blit(text, (textRect.x-outline_thickness,textRect.y-outline_thickness))
      text = bigfont.render(diff, True, 'white', None)
      screen.blit(text, textRect)
      if animated:
        if (fetch_counter+1) <= fps/2:
          pygame.draw.rect(screen, 'green', pygame.Rect((fetch_counter+1)*width/fps*2, 0, width, height))
        if (fetch_counter+1) >= fetch_freq-fps/2:
          pygame.draw.rect(screen, 'green', pygame.Rect((fetch_freq-(fetch_counter+1))*width/fps*2, 0, width, height))
      pygame.draw.rect(screen, 'white', pygame.Rect(frame_x,frame_y,frame_width,frame_height),  4, 10)  
      fetch_counter = (fetch_counter+1)%fetch_freq
      if fetch_counter == 0:
        if auto_mode:
          pred_race = True
          daily_growth = False
          if dead_time_on:
            dead_time = True
            pred_race = False

    if dead_time:
      screen.fill('green')
      fetch_counter = (fetch_counter+1)%dt_freq
      if fetch_counter == 0:
        pred_race = True
        daily_growth = False
        dead_time = False

    # --- main menu logic ---
    if main_menu:
      screen.fill('black')
      screen.blit(apexlogo, (width//2-apexlogo.get_rect().w//2, 10))
      screen.blit(twitchlogo, (width//2-twitchlogo.get_rect().w//2, 11*height//16))
      #start_button.draw(screen, 2)
      get_user_button.draw(screen, 2)
      enter_user_button.draw(screen, 2)

      if get_user_button.isOver(pygame.mouse.get_pos()):
        get_user_button.color = 'orange'
      if not get_user_button.isOver(pygame.mouse.get_pos()):
        get_user_button.color = 'red'

      if enter_user_button.isOver(pygame.mouse.get_pos()):
        enter_user_button.color = 'orange'
      if not enter_user_button.isOver(pygame.mouse.get_pos()):
        enter_user_button.color = 'red'

      screen.blit(dev_text, dev_textRect)
      screen.blit(dev_text2, dev_text2Rect)
      screen.blit(version_text, version_textRect)

    # --- enter user ID menu logic ---
    if enter_user_menu:
      screen.fill('black')
      if input_box1.final_text != None:
        user_text_input = input_box1.final_text
        uid = user_text_input
        if uid != None and uid.isnumeric():
          player_info = get_player_name_and_rank(str(uid))
          if player_info != None:
            player_name = player_info[0]
            player_rank = player_info[1]
            player_div = player_info[2]
            player_RP = player_info[3]
            player_ladderpos = player_info[4]
            player_starting_RP = player_RP
          fetch_counter = 0
        else:
          player_info = None
      if uid != None and uid != '' and player_info != None:
        text = font.render(f'ID: {uid}', True, 'red', 'black')
        textRect = text.get_rect()
        textRect.center = (width // 2, 5*height//16)
        usertext = font.render(f'{player_name}', True, 'red', 'black')
        usertextRect = usertext.get_rect()
        usertextRect.center = (width // 2, 7*height//16)
        screen.blit(text, textRect)
        screen.blit(usertext, usertextRect)
        logo = get_logo_for_rank(player_rank, player_div)
        if logo != None:
          screen.blit(logo,((width // 2)-logo.get_rect().w//2, 8*height//16))
        confirm_user_button.draw(screen, 2)
        if confirm_user_button.isOver(pygame.mouse.get_pos()):
          confirm_user_button.color = 'orange'
        if not confirm_user_button.isOver(pygame.mouse.get_pos()):
          confirm_user_button.color = 'teal'
      screen.blit(inst2_text, inst2_textRect)
      for box in input_boxes:
        box.update()
      for box in input_boxes:
        box.draw(screen)

    # --- find user ID menu logic ---
    if get_user_ID_menu:
      screen.fill('black')
      if input_box1.final_text != None:
        user_text_input = input_box1.final_text
        uid = get_user_ID(user_text_input)
        if uid != None:
          player_info = get_player_name_and_rank(str(uid))
          if player_info != None:
            player_name = player_info[0]
            player_rank = player_info[1]
            player_div = player_info[2]
            player_RP = player_info[3]
            player_ladderpos = player_info[4]
            player_starting_RP = player_RP
          fetch_counter = 0
      if uid == None:
        text = font.render('User not found', True, 'red', 'black')
        textRect = text.get_rect()
        textRect.center = (width // 2, 5*height//16)  
        screen.blit(text, textRect)
      if uid != None and uid != '' and player_info != None:
        text = font.render(f'ID: {uid}', True, 'red', 'black')
        textRect = text.get_rect()
        textRect.center = (width // 2, 5*height//16)
        usertext = font.render(f'{player_name}', True, 'red', 'black')
        usertextRect = usertext.get_rect()
        usertextRect.center = (width // 2, 7*height//16)
        screen.blit(text, textRect)
        screen.blit(usertext, usertextRect)
        logo = get_logo_for_rank(player_rank, player_div)
        if logo != None:
          screen.blit(logo,((width // 2)-logo.get_rect().w//2, 8*height//16))
        confirm_user_button.draw(screen, 2)
        if confirm_user_button.isOver(pygame.mouse.get_pos()):
          confirm_user_button.color = 'orange'
        if not confirm_user_button.isOver(pygame.mouse.get_pos()):
          confirm_user_button.color = 'teal'
      screen.blit(inst_text, inst_textRect)
      for box in input_boxes:
        box.update()
      for box in input_boxes:
        box.draw(screen)

    pygame.display.flip()
    fpsClock.tick(fps)

main()