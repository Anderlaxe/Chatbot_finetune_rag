import { MessageProps } from "../Message";

export type MessagesStorage = Array<(MessageProps & {
    timestamp: number;
  })>;

export type ChatbotLayoutProps = {
    onClose : VoidFunction;
    onSubmit: (message: string) => void;
    loading: boolean;
    messages: MessagesStorage;
}
