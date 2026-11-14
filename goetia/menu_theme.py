"""Pantheon menus, using the supplied illustrated UI and live catalog data."""
import pygame
from .catalog import CHARACTERS, ELEMENTS, SPELLS, MAPS, PASSIVES
from .progression import passive_description


class MenuTheme:
    SIZE = (1672, 941)

    def __init__(self, ui):
        self.ui = ui
        self.cache = {}

    def art(self, name, size):
        key = (name, tuple(size))
        if key not in self.cache:
            self.cache[key] = pygame.transform.smoothscale(self.ui.assets.sheet('images/ui/'+name+'.png'),size)
        return self.cache[key]

    def frame(self, surface, rect, color='#caa65e'):
        pygame.draw.rect(surface,color,rect,2)
        pygame.draw.rect(surface,color,rect.inflate(-10,-10),1)
        for x, dx in ((rect.left,1),(rect.right,-1)):
            for y, dy in ((rect.top,1),(rect.bottom,-1)):
                pygame.draw.lines(surface,color,False,[(x+dx*30,y),(x+dx*12,y+dy*12),(x,y+dy*30)],2)
                pygame.draw.polygon(surface,color,[(x+dx*8,y),(x+dx*15,y+dy*8),(x+dx*8,y+dy*16),(x,y+dy*8)],1)

    def title(self, surface, rect, size):
        # Live title plaque covers the former title embedded in the supplied art.
        texture=self.ui.assets.sheet('images/ui/ice_witch.png').subsurface((570,455,830,40))
        surface.blit(pygame.transform.smoothscale(texture,rect.size),rect)
        self.frame(surface,rect)
        self.ui.text(surface,'PANTHEON',(rect.centerx+2,rect.centery+4),size,'#30200b',True)
        self.ui.text(surface,'PANTHEON',rect.center,size,'#f4d58c',True)

    def info(self, character_id):
        char=CHARACTERS[character_id]
        spell=SPELLS[char['starting_spell']]['name']
        buff=SPELLS[char['buff_spell']]['name']
        key=('info',character_id,char['hp'],char['speed'],char['damage_bonus'],char['cooldown_bonus'],spell,buff)
        reference_values = {
            'ice_witch': (100,180,.25,0,'hyorinmaru'),
            'shadow_monarch': (100,190,.3,0,'shadow_spikes'),
            'light_elf': (95,185,.2,.1,'judgement'),
            'flame_pirate': (120,175,.3,0,'hiken'),
            'lightning_assassin': (90,210,0,.25,'static_needles'),
        }
        hp,speed,damage,cooldown,starting = reference_values[character_id]
        if ((char['hp'],char['speed'],char['damage_bonus'],char['cooldown_bonus']) == (hp,speed,damage,cooldown)
                and char['starting_spell'] == char['buff_spell'] == starting):
            return self.art(character_id,(1536,1024))
        if key not in self.cache:
            panel=self.art(character_id,(1536,1024)).copy()
            texture=panel.subsurface((1320,450,100,30)).copy()
            panel.blit(pygame.transform.smoothscale(texture,(930,430)),(550,45))
            color=ELEMENTS[char['element']]['color']
            self.ui.text(panel,char['name'],(565,57),65,color)
            pygame.draw.line(panel,'#bb9856',(565,150),(1450,150),2)
            self.ui.text(panel,f"Vida: {char['hp']}   |   Velocidade: {char['speed']}",(580,169),42,'#eee3cb')
            pygame.draw.line(panel,'#bb9856',(565,232),(1450,232),2)
            self.ui.wrapped_text(panel,'Magia inicial: '+spell,pygame.Rect(580,278,865,90),40,'#eee3cb')
            bonuses=[]
            if char['damage_bonus']:
                bonuses.append(f"+{char['damage_bonus']*100:g}% dano")
            if char['cooldown_bonus']:
                bonuses.append(f"-{char['cooldown_bonus']*100:g}% recarga")
            self.ui.wrapped_text(panel,'Bônus exclusivo: '+' / '.join(bonuses)+' em '+buff+'.',pygame.Rect(580,368,865,110),39,'#efc366')
            self.cache[key]=panel
        return self.cache[key]

    def draw(self, surface, page):
        ui=self.ui
        canvas=self.art('home-pantheon' if page in ('home','book') else 'selection-pantheon',self.SIZE).copy()
        buttons=[]
        if page=='book':
            self.book(canvas,buttons)
        elif page=='home':
            for i, action in enumerate(('select','select','book','options','quit')):
                buttons.append((pygame.Rect(1180,262+i*98,410,82),action))
        else:
            for i,(key,char) in enumerate(CHARACTERS.items()):
                rect=pygame.Rect(158+i*275,269,266,140)
                canvas.fill('#0b1012',rect)
                self.frame(canvas,rect,ELEMENTS[char['element']]['color'] if key==ui.character_id else '#a78a53')
                portrait=self.art(key,(1536,1024)).subsurface((140,55,390,440))
                portrait=pygame.transform.smoothscale(portrait,(78,88))
                canvas.blit(portrait,portrait.get_rect(midtop=(rect.centerx,rect.y+10)))
                ui.text(canvas,char['name'],(rect.centerx,rect.bottom-22),21,'#eee5d1',True)
                buttons.append((rect,'character:'+key))
            panel=pygame.transform.smoothscale(self.info(ui.character_id),(594,400))
            canvas.blit(panel,(94,429))
            for i,key in enumerate(MAPS):
                rect=pygame.Rect(727+i*280,500,266,173)
                if key==ui.map_id:
                    self.frame(canvas,rect,'#f5d68d')
                buttons.append((rect,'map:'+key))
            for i,(label,seconds) in enumerate((('RÁPIDO · 5 min',300),('MÉDIO · 10 min',600),('COMPLETO · 15 min',900))):
                rect=pygame.Rect(729+i*280,699,261,43)
                canvas.fill('#282012' if ui.duration==seconds else '#101415',rect.inflate(6,8))
                self.frame(canvas,rect,'#ffe5a4' if ui.duration==seconds else '#b99a5b')
                ui.text(canvas,label,rect.center,23,'#f3e3bb',True)
                buttons.append((rect,'duration:'+str(seconds)))
            buttons += [(pygame.Rect(104,851,220,53),'home'),(pygame.Rect(1219,850,375,61),'start')]
        # Uniform scaling keeps art and hit areas aligned at every window size.
        scale=min(surface.get_width()/self.SIZE[0],surface.get_height()/self.SIZE[1])
        size=(round(self.SIZE[0]*scale),round(self.SIZE[1]*scale))
        origin=((surface.get_width()-size[0])//2,(surface.get_height()-size[1])//2)
        mouse=pygame.mouse.get_pos()
        for rect,action in buttons:
            screen_rect=pygame.Rect(round(origin[0]+rect.x*scale),round(origin[1]+rect.y*scale),round(rect.w*scale),round(rect.h*scale))
            if screen_rect.collidepoint(mouse):
                self.frame(canvas,rect.inflate(-4,-4),'#ffedbc')
            ui.buttons.append((screen_rect,action))
        surface.fill('#070a0c')
        surface.blit(pygame.transform.smoothscale(canvas,size),origin)

    def ornate_panel(self, canvas, rect):
        canvas.fill('#101416',rect)
        self.frame(canvas,rect,'#b89451')
        source=self.art('light_elf',(1536,1024))
        for x,y,sx,sy in ((rect.x,rect.y,0,0),(rect.right-40,rect.y,1456,0),
                          (rect.x,rect.bottom-40,0,944),(rect.right-40,rect.bottom-40,1456,944)):
            corner=pygame.transform.smoothscale(source.subsurface((sx,sy,80,80)),(40,40))
            canvas.blit(corner,(x,y))

    def book(self, canvas, buttons):
        ui=self.ui
        shade=pygame.Surface(self.SIZE,pygame.SRCALPHA)
        shade.fill((3,7,9,250))
        canvas.blit(shade,(0,0))
        ui.text(canvas,'PANTHEON',(836,48),44,'#e9ca83',True)
        ui.text(canvas,'GRIMÓRIO DOS ELEMENTOS',(836,100),30,'#f2e6ce',True)
        keys=list(ELEMENTS)
        selected=keys[ui.book_page]
        for i,key in enumerate(keys):
            rect=pygame.Rect(145+i*280,143,262,47)
            canvas.fill('#2c2518' if key==selected else '#0e1316',rect)
            self.frame(canvas,rect,ELEMENTS[key]['color'] if key==selected else '#9b7b41')
            ui.text(canvas,ELEMENTS[key]['name'].upper(),rect.center,23,ELEMENTS[key]['color'],True)
            buttons.append((rect,'book_element:'+key))
        entries=[(k,v) for k,v in SPELLS.items() if v['element']==selected]
        entries += [(k,v) for k,v in PASSIVES.items() if v['element']==selected]
        for i,(key,data) in enumerate(entries):
            rect=pygame.Rect(100+i%3*497,215+i//3*305,478,286)
            self.ornate_panel(canvas,rect)
            color=ELEMENTS[selected]['color']
            icon_rect=pygame.Rect(rect.x+23,rect.y+22,84,84)
            self.frame(canvas,icon_rect,color)
            icon=ui.assets.item_icon(key,(70,70))
            canvas.blit(icon,(icon_rect.x+7,icon_rect.y+7))
            is_spell=key in SPELLS
            ui.text(canvas,'MAGIA' if is_spell else 'ITEM PASSIVO',(rect.x+125,rect.y+25),16,color)
            ui.wrapped_text(canvas,data['name'],pygame.Rect(rect.x+120,rect.y+65,rect.w-142,50),24,'#f1e5cd')
            description=data['description'] if is_spell else passive_description(key)
            ui.wrapped_text(canvas,description,pygame.Rect(rect.x+24,rect.y+130,rect.w-48,75),18,'#c5c0b3')
            pygame.draw.line(canvas,'#665638',(rect.x+25,rect.y+199),(rect.right-25,rect.y+199))
            if is_spell:
                partner=data['passive']
                label='EVO: '+data['evolution']
                detail='Requer '+PASSIVES[partner]['name']
            else:
                partner=next((k for k,v in SPELLS.items() if v['passive']==key),None)
                label='EVOLUI '+SPELLS[partner]['name'] if partner else 'BÔNUS PASSIVO'
                detail=SPELLS[partner]['evolution'] if partner else 'Melhora os atributos do personagem.'
            if partner:
                icon=ui.assets.item_icon(partner,(40,40))
                canvas.blit(icon,(rect.x+24,rect.y+222))
            ui.wrapped_text(canvas,label,pygame.Rect(rect.x+74,rect.y+222,rect.w-95,25),17,'#efc97b')
            ui.wrapped_text(canvas,detail,pygame.Rect(rect.x+74,rect.y+249,rect.w-95,25),16,'#b5b8ba')
        for label,rect,action in [('VOLTAR',pygame.Rect(100,854,230,52),'home'),
                                  ('ANTERIOR',pygame.Rect(560,854,230,52),'book_prev'),
                                  ('PRÓXIMO',pygame.Rect(886,854,230,52),'book_next')]:
            self.ornate_panel(canvas,rect)
            ui.text(canvas,label,rect.center,23,'#eddbb5',True)
            buttons.append((rect,action))
        ui.text(canvas,f'{ui.book_page+1} / 5',(838,880),21,'#d9bd7f',True)
        ui.text(canvas,'15 magias · 15 passivas',(1395,880),22,'#b7a98d',True)
