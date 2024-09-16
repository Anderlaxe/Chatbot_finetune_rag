import { Box, Card, useTheme } from "@mui/material";
import { InputBox } from "../InputBox/InputBox";
import TopBar from "../TopBar/TopBar";
import { Message } from "../Message";
import { ChatbotLayoutProps } from "./types";
import { List, AutoSizer, CellMeasurer, CellMeasurerCache } from 'react-virtualized';
import { useEffect, useRef } from "react";

export const ChatbotLayout = ({ onClose, messages, onSubmit, loading }: ChatbotLayoutProps) => {
  const theme = useTheme();

  const listRef = useRef<List>(null);
  useEffect(() => {
    listRef.current?.scrollToRow(messages.length - 1);
  }, [messages]);


  const cache = new CellMeasurerCache({
    fixedWidth: true,
    defaultHeight: 100
  });

  const renderRow = ({ index, key, style, parent }: any) => {
    return (
      <CellMeasurer
        key={key}
        cache={cache}
        parent={parent}
        columnIndex={0}
        rowIndex={index}>
        {({registerChild}: any) => (
          <Box ref={registerChild} style={style}>
            <Message {...messages[index]}/> 
          </Box>
        )}
      </CellMeasurer>
    )
  }

  return (
    <Card sx={{
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "stretch",
        height: "400px",
        width: "300px",
        bgcolor: theme.palette.common.white,
        borderTopLeftRadius: theme.spacing(2),
        borderTopRightRadius: theme.spacing(2),
        borderBottomLeftRadius: theme.spacing(2),
        borderBottomRightRadius: theme.spacing(1),
        boxShadow: theme.shadows[4],
    }}>
        <TopBar onClose={onClose} />
        <Box sx={{
            display: "flex",
            flexDirection: "column",
            alignItems: "stretch",
            justifyContent: "flex-start",
            flex: 1,
            paddingX: theme.spacing(1),
            paddingY: theme.spacing(2),
            overflowY: "auto"
        }}>
          <AutoSizer>
            {
              ({ width, height }) => (<List
                  ref={listRef}
                  width={width}
                  height={height}
                  deferredMeasurementCache={cache}
                  rowHeight={cache.rowHeight}
                  rowRenderer={renderRow}
                  rowCount={messages.length}
                  overscanRowCount={3} />
              )
            }
          </AutoSizer>
        </Box>
        <InputBox onSubmit={onSubmit} loading={loading}/>
    </Card>
  );
};
