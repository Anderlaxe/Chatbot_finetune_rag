import SpeedDialIcon from '@mui/material/SpeedDialIcon';
import HelpIcon from '@mui/icons-material/Help';
import { Collapse, SpeedDial } from '@mui/material';
import { ChatbotLayout, MessagesStorage } from '../ChatbotLayout';
import { useCallback, useEffect, useRef, useState } from 'react';
import { Variant } from '../Message';

const OLD_ENOUGH = 1000 * 30;

let i = 0
function generateBotComment(): Promise<string> {
  const comments = [
    "Bonjour, je suis Chatbot, l'assistant virtuel de l'université ! Comment puis-je vous aider ?",
    "Laissez moi réflechir... Sur quel campus êtes-vous ?",
    "Parfait ! Vous pouvez aller manger à la caféteria du CROUS ou dans les restaurants à proximité."
  ];
  const com = comments[i++ % comments.length];
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(com);
    }, Math.random() * 2000);
  });
}

export const Chatbot = () => {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<MessagesStorage>([]);
  const messagesRef = useRef<MessagesStorage>(messages);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    messagesRef.current = messages;
  }, [messages]);

  const storeMessage = useCallback((content: string, variant: Variant) => {
    const timestamp = Date.now();
    if (messagesRef.current[messagesRef.current.length - 1]?.variant === variant) {
      let index = messagesRef.current.length - 1;
      while (index > 0 && messagesRef.current[index]?.variant === variant && messagesRef.current[index].isFollowup) {index--;}
      const groupTimestamp = messagesRef.current[index]?.timestamp;
      if (messagesRef.current[index]?.variant !== variant || timestamp - groupTimestamp > OLD_ENOUGH) {
        setMessages((prev) => [
          ...prev,
          { variant, content, timestamp, isFollowup: false },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          { variant, content, timestamp, isFollowup: true },
        ]);
      }
    } else {
      setMessages((prev) => [
        ...prev,
        { variant, content, timestamp, isFollowup: false },
      ]);
    }
  }, [setMessages, messagesRef]);


  const submit = async (content: string) => {
    if (content.replace(/(\r\n|\n|\r)/gm, "").length === 0) return;

    storeMessage(content, Variant.USER);
    setLoading(true);
    const botComment = await generateBotComment();
    setLoading(false);
    storeMessage(botComment, Variant.BOT);
  }

  
  return (
    <SpeedDial
      ariaLabel="AI chatbot"
      sx={{ position: "absolute", bottom: 16, right: 16, alignItems: "flex-end" }}
      icon={<SpeedDialIcon openIcon={<HelpIcon />} />}
      open={open}
      FabProps={{
        onClick: () => setOpen(!open),
      }}
      
    >
      <Collapse in={open}>
        <ChatbotLayout onClose={() => setOpen(false)} onSubmit={submit} loading={loading} messages={messages}/>
      </Collapse>
    </SpeedDial>
  );
};
