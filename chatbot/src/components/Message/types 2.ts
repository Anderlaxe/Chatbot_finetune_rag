export enum Variant {
    USER,
    BOT
}

export type MessageProps = {
    variant: Variant,
    content: string,
    isFollowup: boolean
}
