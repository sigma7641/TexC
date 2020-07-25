# 
# TexC
# 
# Copyright (c) 2020 sigma7641
# 
# This software is released under the MIT.
# see https://opensource.org/licenses/MIT
# 
import re
import logging
import sys
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
def main():
    logger.info('Hello! This is TexC.')
    filenames = sys.argv
    fName = filenames[1]
    logger.info("This file name is "+ fName)
# ファイルの読み込み
    if len(filenames) == 2:
        with open(fName,mode='r',encoding='utf-8') as f:
          fContent = f.read()
        cp = SimpleDocument(fName, fContent)
        outstr, outTitle = cp.processing(fContent, fName)

    # ファイルの書き出し
        with open(outTitle+'.txt', mode='w',encoding='utf-8') as f:
          f.write(outstr)
          logger.info("Out put " + outTitle)
    elif len(filenames) >= 3:
        with open(fName,mode='r',encoding='utf-8') as f:
          fContent = f.read()
        cp = SimpleDocument(fName, fContent)
        ft_no_comment = cp.commentOut(fContent)
        cp.extpreamble(ft_no_comment)
        cp.makeCommands(cp.preamble)
        cp.body = cp.extbody(ft_no_comment)
        # cp.initialize()
        for tprename in filenames[2:]:
          with open(tprename,mode='r',encoding='utf-8') as f:
            tpreamble = f.read()
          ft_no_comment = cp.commentOut(tpreamble)
          cp.extpreamble(ft_no_comment)
          cp.makeCommands(cp.preamble)
          replaced_body = cp.makeBody(cp.body)
          #formatting
          cp.fs_out = cp.formatting(replaced_body)
          outTitle = cp.commands["title"]
          with open(outTitle + '.txt', mode='w',encoding='utf-8') as f:
            f.write(cp.fs_out)
            logger.info("Out put " + outTitle)

class TexC:
  symbol = locals()
  def __init__(self, fName, content):
    self.fName = fName
    self.content = content
    self.commands = {'%':'%'}
    self.keys = ["title", "author", "organization"]
    logger.info("Start compling "+ fName)
  def initialize(self):
    self.commands = {'%':'%'}
    self.keys = ["title", "author", "organization"]
    return True
  def processing(self, ft, fName):
      #コメントを取り除く
      ft_no_comment = self.commentOut(ft)
      #メタデータ読み取り
      self.extpreamble(ft_no_comment)
      self.makeCommands(self.preamble)
      self.body = self.extbody(ft_no_comment)
      replaced_body = self.makeBody(self.body)
      #formatting
      self.fs_out = self.formatting(replaced_body)
      return self.fs_out, self.commands['title']
        
  def extpreamble(self, ft):
      preambleObj = re.search(r'.*(?=\n*\\begin{document})',ft,flags=(re.DOTALL))
      if preambleObj:
        preamble = preambleObj.group()
      else:
        preamble = ft
      self.preamble = re.sub(r':\n','',preamble)
      return True

  def extbody(self, ft):
      bodyObj = re.search(r'(?<=\\begin{document}).*(?=\\end{document})',ft, flags=(re.DOTALL))
      if bodyObj:
        body = bodyObj.group()
      else:
        body = "This file doesn't have document environment."
      return body

  def makeCommands(self, preamble):
      preamble_no_bl = re.sub('\n\n+','',preamble)
      lines = preamble.split('\n')
      for line in lines:
        keyObj = re.search(r'(?<=^\\).*?(?={)',line)
        if keyObj == None:
          continue
        key = keyObj.group()
        if key in self.commands:
          logger.info("There already exited "+key+" and it is redifined.")
        recmd = re.compile('(?<={).*?(?=})')
        cmdargs = recmd.findall(line)
        keyjudge = lambda x: "defc" if x in self.keys else key
        self.symbol[keyjudge(key)](self,key,*cmdargs)
      return True

  def exeCommnd(self, command, *argv):
      exitsCommand = re.search('\\\\.*(?=[\\\\\\n ]|$)')
      # if exeCommnd:

  def makeBody(self, body):
      split_body = re.findall('.*\n',body)
      rep_body = ''
      # search_command = r'\\[\\a-zA-Z]+?(?=[\(\n) ])?'
      search_command = r'(?<=\\)[a-zA-Z]+(?=[\(\n) ])?'
      search_command_compiled = re.compile(search_command)
      for line in split_body:
        exits_cmd= re.findall(search_command,line)
        rep_line = line
        for cmd in exits_cmd:
          t_search_b = r'\\'+repr(cmd)[1:-1]+' ?'
          t_search = re.compile(t_search_b)
          rep_line= re.sub(t_search,self.commands[cmd],rep_line)
        rep_body += rep_line
      return rep_body

  def commentOut(self, ft):
      #コメント処理 %以降行末までコメント %直前の任意個の空白タブも認識されない
      ft_out =  re.sub('^[ \t]*%.*\n?','',ft)
      ft_out =  re.sub('(?<=[\n])[ \t]*%.*\n?','',ft_out)
      ft_out = re.sub('(?<!^)[ \t]*%.*\n','\n',ft_out)
      return ft_out
  def formatting(self, ft):
      #3回以上連続の改行でないと改行されない
      ft_out = re.sub('\n[ \t]*\n+','%n',ft)
      ft_out = re.sub(r'\\\\','%n',ft_out)
      ft_out = re.sub('\n','',ft_out)
      ft_out = re.sub('%n','\n',ft_out)
      return ft_out

class SimpleDocument(TexC):
  symbol = locals()
  def __init__(self, fName, content):
    super().__init__(fName, content)
    self.keys.append(["newcommand","defc"])
    self.commands["defc"] = "defc"
  def newcommand(self,key,arg1,arg2):
      if arg1 in self.commands:
        logger.info("There already exited "+arg1+" and it is redifined.")
      self.commands[arg1] = arg2
      return True
  def defc(self,key,arg1):
      self.commands[key] = arg1
      return True
if __name__ == '__main__':
  main()