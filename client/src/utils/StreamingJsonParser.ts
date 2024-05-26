/**
 * ==============================================
 * All credit to https://github.com/clue/json-stream/blob/master/src/StreamingJsonParser.php
 * ==============================================
 */

export default class StreamingJsonParser {
    constructor() {
        this.buffer = '';
        this.endCharacter = null;
        this.assoc = true;
    }

    parse(chunk) {
        const objects = [];

        while (chunk !== '') {
            if (this.endCharacter === null) {
                chunk = chunk.trim();

                if (chunk === '') {
                    break;
                } else if (chunk[0] === '[') {
                    this.endCharacter = ']';
                } else if (chunk[0] === '{') {
                    this.endCharacter = '}';
                } else {
                    throw new Error('Invalid start');
                }
            }

            const pos = chunk.indexOf(this.endCharacter);

            if (pos === -1) {
                this.buffer += chunk;
                break;
            }

            this.buffer += chunk.substring(0, pos + 1);
            chunk = chunk.substring(pos + 1);

            let json;
            try {
                json = JSON.parse(this.buffer);
            } catch (error) {
                continue;
            }

            if (json !== undefined) {
                objects.push(json);

                this.buffer = '';
                this.endCharacter = null;
            }
        }

        return objects;
    }

    isEmpty() {
        return (this.buffer === '');
    }
}
