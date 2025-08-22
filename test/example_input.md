## Form Table

| Form label              | value                       |
|-------------------------|------------------------------|
| actionNameToCreate      | integration-test-04         |
| bpm                     | 96                          |
| beatsPerBar             | 4                           |
| blendFileToOutputAction | test_output/actions.blend   |
| poseBlendFile           | dobby-poses.blend           |
| poseCatalog             | k3                          |
| midiFile                | assets/eight-bars-thang.mid |

## Dance Table

| poseCatalog | track  | cycle mode   | interpolation | preHold | postHold |
|-------------|--------|--------------|---------------|---------|----------|
| hips        | shaker | random       | back          | 2       | 5        |
| feet        | horns  | loop         | quartic       |         |          |
| hands       | quack  | pitch_follow | quartic       |         | 3        |
| head        | sub    | pitch_follow | bezier        |         | 0        |